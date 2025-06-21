from datetime import timedelta
from typing import Final, final

from asgiref.sync import sync_to_async
from django.http.request import HttpRequest
from django.utils import timezone
from expression import Option

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, acontext_result
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
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

    @acontext_result
    async def asynchronize(self) -> ContextResult[str]:
        return (
            await self.__get_signed_user_id()
            .bind(self.__user_service.unsign_id)
            .abind(self.__adelete_expired_data)
            .aor_else(
                self.__aget_or_create_session()
                .abind(self.__aget_or_create_user)
                .amap(self.__aset_signed_user_id_and_expiry)
                .bind(self.__user_service.unsign_id)
                .abind(self.__adelete_expired_data)
            )
        )

    @acontext_result
    async def __get_signed_user_id(self) -> ContextResult[str]:
        try:
            return ContextResult[str].from_result(
                Option[str]
                .of_optional(await self.__request.session.aget(self.__user_id_key, None))
                .to_result(ErrorContext.not_found(f"{self.__user_id_key} not found in session"))
            )
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to get {self.__user_id_key} from session")
            await self.__aclear()
            return ContextResult[str].failure(ErrorContext.server_error())

    @acontext_result
    async def __aget_or_create_session(self) -> ContextResult[str]:
        return await self.__get_session_key().aor_else(
            self.__acreate_session().bind(lambda _: self.__get_session_key())
        )

    def __get_session_key(self) -> ContextResult[str]:
        try:
            return ContextResult[str].from_result(
                Option[str]
                .of_optional(self.__request.session.session_key)
                .to_result(ErrorContext.not_found("Session key not found"))
            )
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to get session key")
            return ContextResult[str].failure(ErrorContext.server_error())

    @acontext_result
    async def __acreate_session(self) -> ContextResult[None]:
        try:
            await self.__aclear()
            await self.__request.session.acreate()
            return ContextResult[None].success(None)
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to create session")
            return ContextResult[None].failure(ErrorContext.server_error())

    @acontext_result
    async def __aget_or_create_user(self, session_key: str) -> ContextResult[AppUser]:
        try:
            session_key_expiration_date = await self.__request.session.aget_expiry_date()
            return await self.__user_repository.aget_or_create_user(session_key, session_key_expiration_date)
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to get or create user")
            await self.__aclear()
            return ContextResult[AppUser].failure(ErrorContext.server_error())

    async def __aset_signed_user_id_and_expiry(self, user: AppUser) -> str:
        try:
            signed_user_id = await self.__request.session.asetdefault(
                self.__user_id_key,
                self.__user_service.sign_id(user.id),
            )
            self.__logger.log_debug(f"Signed {self.__user_id_key} '{signed_user_id}' has been set")

            await self.__request.session.aset_expiry(timedelta(minutes=15))
            session_expiry_date = await self.__request.session.aget_expiry_date()
            self.__logger.log_debug(f"Session expiry date has been set to {session_expiry_date}")

            return str(signed_user_id)
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to set {self.__user_id_key} in session")
            await self.__aclear()
            return ""

    @acontext_result
    async def __adelete_expired_data(self, user_id: str) -> ContextResult[str]:
        def log_success(value: str) -> str:
            self.__logger.log_info(f"Data for User '{value}' have been removed")
            return value

        def log_error(error: ErrorContext) -> ErrorContext:
            self.__logger.log_error(error.message)
            return error

        return (
            await self.__editor_repository.aget_original_asset(user_id)
            .amap(lambda original: original.adelete())
            .map(lambda _: self.__logger.log_debug(f"Editor: Original asset of User '{user_id}' has been deleted "))
            .abind(lambda _: self.__editor_repository.aget_edited_asset(user_id))
            .amap(lambda edited: edited.adelete())
            .map(lambda _: self.__logger.log_debug(f"Editor: Edited asset of User '{user_id}' has been deleted "))
            .abind(lambda _: self.__converter_repository.aget_asset(user_id))
            .amap(lambda converted: converted.adelete())
            .map(lambda _: self.__logger.log_debug(f"Converter: Asset of User '{user_id}' has been deleted "))
            .abind(lambda _: self.__cloudinary_service.adelete_files(user_id, "converter"))
            .abind(lambda _: self.__cloudinary_service.adelete_files(user_id, "editor"))
            # TODO: delete folders
            .amap(lambda _: self.__request.session.aclear_expired())
            .map(lambda _: user_id)
            .match(log_success, log_error)
            if await self.__ais_expired()
            else ContextResult[str].success(user_id)
        )

    async def __ais_expired(self) -> bool:
        try:
            session_expiry_date = await self.__request.session.aget_expiry_date()
            return timezone.now() > session_expiry_date
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to check if session expired")
            await self.__aclear()
            return True

    async def __aclear(self) -> None:
        return await sync_to_async(self.__request.session.clear)()
