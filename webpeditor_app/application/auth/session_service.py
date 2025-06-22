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
from webpeditor_app.globals import Unit
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
                .abind(self.__aset_signed_user_id_and_expiry)
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
    async def __acreate_session(self) -> ContextResult[Unit]:
        try:
            await self.__aclear()
            await self.__request.session.acreate()
            return ContextResult[Unit].success(Unit())
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to create session")
            return ContextResult[Unit].failure(ErrorContext.server_error())

    @acontext_result
    async def __aget_or_create_user(self, session_key: str) -> ContextResult[AppUser]:
        try:
            session_key_expiration_date = await self.__request.session.aget_expiry_date()
            return await self.__user_repository.aget_or_create(session_key, session_key_expiration_date)
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to get or create user")
            await self.__aclear()
            return ContextResult[AppUser].failure(ErrorContext.server_error())

    @acontext_result
    async def __aset_signed_user_id_and_expiry(self, user: AppUser) -> ContextResult[str]:
        try:
            signed_user_id = await self.__request.session.asetdefault(
                self.__user_id_key,
                self.__user_service.sign_id(user.id),
            )
            self.__logger.log_debug(f"Signed User ID '{signed_user_id}' has been set")

            await self.__request.session.aset_expiry(timedelta(minutes=15))
            session_expiry_date = await self.__request.session.aget_expiry_date()
            self.__logger.log_debug(f"Session expiry date has been set to {session_expiry_date}")

            return ContextResult[str].success(str(signed_user_id))
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to set {self.__user_id_key} in session")
            await self.__aclear()
            return ContextResult[str].failure(ErrorContext.server_error("Session is corrupted"))

    @acontext_result
    async def __adelete_expired_data(self, user_id: str) -> ContextResult[str]:
        def log_success(value: str) -> str:
            self.__logger.log_info(f"Data for User '{value}' have been removed")
            return value

        def log_error(error: ErrorContext) -> ErrorContext:
            self.__logger.log_error(error.message)
            return error

        return await self.__ais_expired().aif_then_else(
            lambda is_expired: not is_expired,
            lambda _: ContextResult[str].success(user_id),
            lambda _: self.__editor_repository.aget_original_asset(user_id)
            .amap(lambda original: original.adelete())
            .map(
                lambda info: self.__logger.log_info(f"Editor: Deleted {info[0]} Original asset(s) for User '{user_id}'")
            )
            .abind(lambda _: self.__editor_repository.aget_edited_asset(user_id))
            .amap(lambda edited: edited.adelete())
            .map(lambda info: self.__logger.log_info(f"Editor: Deleted {info[0]} Edited asset(s) for User '{user_id}'"))
            .abind(lambda _: self.__converter_repository.aget_asset(user_id))
            .amap(lambda converted: converted.adelete())
            .map(lambda info: self.__logger.log_info(f"Converter: Deleted {info[0]} Asset(s) for User '{user_id}'"))
            .abind(lambda _: self.__cloudinary_service.adelete_resource_recursively(user_id, "converter"))
            .abind(lambda _: self.__cloudinary_service.adelete_resource_recursively(user_id, "editor"))
            .amap(lambda _: self.__request.session.aclear_expired())
            .map(lambda _: user_id)
            .match(log_success, log_error),
        )

    @acontext_result
    async def __ais_expired(self) -> ContextResult[bool]:
        try:
            session_expiry_date = await self.__request.session.aget_expiry_date()
            return ContextResult[bool].success(timezone.now() > session_expiry_date)
        except Exception as exception:
            self.__logger.log_exception(exception, "Failed to check if session expired")
            await self.__aclear()
            return ContextResult[bool].failure(ErrorContext.server_error("Session is corrupted"))

    async def __aclear(self) -> None:
        return await sync_to_async(self.__request.session.clear)()
