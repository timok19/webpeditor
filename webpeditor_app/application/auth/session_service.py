import math
from datetime import timedelta
from typing import Final, final

from django.http.request import HttpRequest
from django.utils import timezone
from expression import Option

from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import AwaitableContextResult, ContextResult, ErrorContext
from webpeditor_app.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.infrastructure import UserRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.models.app_user import AppUser


@final
class SessionService:
    def __init__(
        self,
        request: HttpRequest,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: WebPEditorLoggerABC,
        editor_repository: EditorRepositoryABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
    ) -> None:
        self.__request: Final[HttpRequest] = request
        self.__user_service: Final[UserServiceABC] = user_service
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__logger: Final[WebPEditorLoggerABC] = logger
        self.__editor_repository: Final[EditorRepositoryABC] = editor_repository
        self.__converter_repository: Final[ConverterRepositoryABC] = converter_repository
        self.__user_repository: Final[UserRepositoryABC] = user_repository
        self.__user_id_key: Final[str] = "USER_ID"

    # TODO: make this method more functional
    async def aasynchronize(self) -> None:
        """
        Updates the session store of current User.

        If the session has expired, it deletes data of the user in the session store.
        """
        await self.__aset_signed_user_id()

        current_expiry_age_minutes: int = await self.__aget_expiry_age_minutes()

        user_id_result = await self.aget_unsigned_user_id()
        if user_id_result.is_error():
            self.__logger.log_error(
                f"Failed to get User ID. Reason: {user_id_result.error.message}. Error code: {user_id_result.error.error_code}"
            )
            return

        session_expiry_date = self.__request.session.get_expiry_date().astimezone(timezone.get_default_timezone())
        if timezone.now() > session_expiry_date:
            await user_id_result.amap(self.__acleanup_storages)

        await self.aset_expiry(timedelta(minutes=15))

        new_expiry_age_minutes: int = await self.__aget_expiry_age_minutes()

        # Log messages
        self.__logger.log_debug(
            f"Current session expiration time of user '{user_id_result.ok}': {current_expiry_age_minutes} minute(s)"
        )
        self.__logger.log_debug(
            f"Updated session expiration time of user '{user_id_result.ok}': {new_expiry_age_minutes} minute(s)"
        )

    def aget_unsigned_user_id(self) -> AwaitableContextResult[str]:
        return self.__aget_signed_user_id().bind(self.__user_service.unsign_id)

    async def aset_expiry(self, duration: timedelta) -> None:
        await self.__request.session.aset_expiry(timezone.now() + duration)

    def aclear_expired(self) -> AwaitableContextResult[None]:
        async def aclear_expired() -> ContextResult[None]:
            user_id_result = await self.aget_unsigned_user_id()
            return await (
                user_id_result.amap(lambda _: self.__request.session.aclear_expired())
                .bind(lambda _: user_id_result)
                .map(lambda user_id: self.__logger.log_info(f"Expired session of User '{user_id}' has been cleared"))
            )

        return AwaitableContextResult(aclear_expired())

    def __aset_signed_user_id(self) -> AwaitableContextResult[str]:
        return (
            self.__aensure_session_exists()
            .abind(lambda _: self.__aget_signed_user_id())
            .aor_else(
                ContextResult[str]
                .from_result(self.__get_session_key().to_result(ErrorContext.not_found()))
                .abind(self.__acreate_app_user)
                .map(lambda user: self.__user_service.sign_id(user.id))
                .amap(self.__aset_signed_user_id_in_session)
            )
        )

    def __aensure_session_exists(self) -> AwaitableContextResult[None]:
        async def aensure_session_exists() -> ContextResult[None]:
            if self.__get_session_key().is_none() or self.__request.session.is_empty():
                await self.__request.session.acreate()
            return ContextResult[None].success(None)

        return AwaitableContextResult(aensure_session_exists())

    def __aget_signed_user_id(self) -> AwaitableContextResult[str]:
        async def aset_signed_user_id() -> ContextResult[str]:
            return ContextResult[str].from_result(
                Option[str]
                .of_optional(str(await self.__request.session.aget(self.__user_id_key)))
                .to_result(ErrorContext.not_found(f"Unable to find signed User ID under key {self.__user_id_key}"))
            )

        return AwaitableContextResult(aset_signed_user_id())

    def __get_session_key(self) -> Option[str]:
        return Option[str].of_optional(self.__request.session.session_key)

    async def __acreate_app_user(self, session_key: str) -> ContextResult[AppUser]:
        session_key_expiration_date = await self.__request.session.aget_expiry_date()
        return await self.__user_repository.acreate_user(session_key, session_key_expiration_date)

    async def __aset_signed_user_id_in_session(self, signed_user_id: str) -> str:
        await self.__request.session.aset(self.__user_id_key, signed_user_id)
        self.__logger.log_debug(f"Signed User ID '{signed_user_id}' has been added into the session storage")
        return signed_user_id

    async def __aget_expiry_age_minutes(self) -> int:
        return math.ceil(await self.__request.session.aget_expiry_age() / 60)

    async def __acleanup_storages(self, user_id: str) -> ContextResult[None]:
        def log_success(_: None) -> None:
            self.__logger.log_info("Storages have been cleaned up")

        def log_error(error: ErrorContext) -> ErrorContext:
            self.__logger.log_error(error.message)
            return error

        return (
            await self.__editor_repository.aget_original_asset(user_id)
            .amap(lambda original: original.adelete())
            .abind(lambda _: self.__editor_repository.aget_edited_asset(user_id))
            .amap(lambda edited: edited.adelete())
            .abind(lambda _: self.__converter_repository.aget_asset(user_id))
            .amap(lambda converted: converted.adelete())
            .map(lambda _: self.__cloudinary_service.delete_original_and_edited_images(user_id))
            .map(lambda _: self.__cloudinary_service.delete_converted_images(user_id))
            .abind(lambda _: self.aclear_expired())
            .match(log_success, log_error)
        )
