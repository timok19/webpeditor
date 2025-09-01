import datetime
from datetime import timedelta
from typing import Any, Final, Union, final, Optional

from asgiref.sync import sync_to_async
from django.http.request import HttpRequest
from django.utils import timezone
from expression import Option

from webpeditor_app.application.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, as_awaitable_result
from webpeditor_app.types import Unit
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.infrastructure.database.models.app_user import AppUser


@final
class SessionService:
    def __init__(
        self,
        request: HttpRequest,
        user_service: UserServiceABC,
        logger: LoggerABC,
        editor_repo: EditorRepositoryABC,
        converter_repo: ConverterRepositoryABC,
        user_repo: UserRepositoryABC,
    ) -> None:
        self.__request: Final[HttpRequest] = request
        self.__user_service: Final[UserServiceABC] = user_service
        self.__logger: Final[LoggerABC] = logger
        self.__editor_repo: Final[EditorRepositoryABC] = editor_repo
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo
        self.__user_repo: Final[UserRepositoryABC] = user_repo
        self.__user_id_key: Final[str] = "USER_ID"

    @as_awaitable_result
    async def asynchronize(self) -> ContextResult[str]:
        return await (
            self.__aget_user_id()
            .abind(lambda user_id: self.__aupdate_session_expiry(user_id).map(lambda _: user_id))
            .aor_else(
                self.__aget_or_create_session()
                .abind(self.__aget_or_create_user)
                .abind(self.__aset_signed_user_id)
                .abind(lambda _: self.__aget_user_id())
            )
        )

    @as_awaitable_result
    async def __aget_user_id(self) -> ContextResult[str]:
        return await self.__aget_signed_user_id().bind(self.__user_service.unsign_id)

    @as_awaitable_result
    async def __aget_signed_user_id(self) -> ContextResult[str]:
        try:
            return ContextResult[str].from_result(
                Option[str]
                .of_optional(await self.__aget(self.__user_id_key))
                .to_result(ErrorContext.not_found(f"{self.__user_id_key} not found in session"))
            )
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to get {self.__user_id_key} from session")
            await self.__aclear()
            return ContextResult[str].failure(ErrorContext.server_error())

    @as_awaitable_result
    async def __aupdate_session_expiry(self, user_id: str) -> ContextResult[Unit]:
        try:
            current_expiry_date = await self.__aget_expiry_date()
            self.__logger.debug(f"Current session expires at '{current_expiry_date}' for User '{user_id}'")

            await self.__aset_expiry(timezone.now() + timedelta(minutes=15))

            updated_expiry_date = await self.__aget_expiry_date()
            self.__logger.debug(f"Updated session expires at '{updated_expiry_date}' for User '{user_id}'")

            return ContextResult[Unit].success(Unit())
        except Exception as exception:
            self.__logger.exception(exception, f"Unable to update session expiry date for User '{user_id}'")
            await self.__aclear()
            return ContextResult[Unit].failure(ErrorContext.server_error())

    @as_awaitable_result
    async def __aget_or_create_session(self) -> ContextResult[str]:
        return await self.__get_session_key().aor_else(self.__acreate_session().bind(lambda _: self.__get_session_key()))

    def __get_session_key(self) -> ContextResult[str]:
        try:
            return ContextResult[str].from_result(
                Option[str]
                .of_optional(self.__request.session.session_key)
                .to_result(ErrorContext.not_found("Session key not found in the session"))
            )
        except Exception as exception:
            self.__logger.exception(exception, "Failed to get session key")
            return ContextResult[str].failure(ErrorContext.server_error())

    @as_awaitable_result
    async def __acreate_session(self) -> ContextResult[Unit]:
        try:
            await self.__aclear()
            await self.__acreate()
            return ContextResult[Unit].success(Unit())
        except Exception as exception:
            self.__logger.exception(exception, "Failed to create session")
            return ContextResult[Unit].failure(ErrorContext.server_error())

    @as_awaitable_result
    async def __aget_or_create_user(self, session_key: str) -> ContextResult[AppUser]:
        try:
            session_key_expiration_date = await self.__aget_expiry_date()
            return await self.__user_repo.aget_or_create(session_key, session_key_expiration_date)
        except Exception as exception:
            self.__logger.exception(exception, "Failed to get or create user")
            await self.__aclear()
            return ContextResult[AppUser].failure(ErrorContext.server_error())

    @as_awaitable_result
    async def __aset_signed_user_id(self, user: AppUser) -> ContextResult[Unit]:
        try:
            signed_user_id = self.__user_service.sign_id(user.id)
            await self.__aset_default(self.__user_id_key, signed_user_id)
            self.__logger.debug(f"Signed User ID '{signed_user_id}' has been set")
            return ContextResult[Unit].success(Unit())
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to set '{self.__user_id_key}' into session")
            await self.__aclear()
            return ContextResult[Unit].failure(ErrorContext.server_error("Session is corrupted"))

    async def __acreate(self) -> None:
        return await sync_to_async(self.__request.session.create)()

    async def __aclear(self) -> None:
        return await sync_to_async(self.__request.session.clear)()

    async def __aget(self, key: str) -> Any:
        return await sync_to_async(self.__request.session.get)(key)

    async def __aset_default(self, key: str, default: Any) -> Any:
        return await sync_to_async(self.__request.session.setdefault)(key, default)

    async def __aget_expiry_date(self) -> datetime.datetime:
        return await sync_to_async(self.__request.session.get_expiry_date)()

    async def __aset_expiry(self, value: Optional[Union[datetime.datetime, int]]) -> None:
        return await sync_to_async(self.__request.session.set_expiry)(value)


# TODO: write separately into scheduled job for cleaning
# @as_awaitable_result
# async def adelete_expired_data(self, user_id: str) -> ContextResult[Unit]:
#     return await self.__ais_expired().aif_then_else(
#         lambda is_expired: not is_expired,
#         lambda _: ContextResult[Unit].asuccess(Unit()),
#         lambda _: self.__editor_repository.aget_original_asset(user_id)
#         .amap(lambda original: original.adelete())
#         .map(lambda info: self.__logger.info(f"Editor: Deleted {info[0]} Original asset(s) for User '{user_id}'"))
#         .abind(lambda _: self.__editor_repository.aget_edited_asset(user_id))
#         .amap(lambda edited: edited.adelete())
#         .map(lambda info: self.__logger.info(f"Editor: Deleted {info[0]} Edited asset(s) for User '{user_id}'"))
#         .abind(lambda _: self.__converter_repository.aget_asset(user_id))
#         .amap(lambda converter_asset: converter_asset.adelete())
#         .map(lambda info: self.__logger.info(f"Converter: Deleted {info[0]} Asset(s) for User '{user_id}'"))
#         .amap(lambda _: sync_to_async(self.__request.session.clear_expired)())
#         .abind(lambda _: self.__converter_files_repository.acleanup(user_id))
#         .abind(lambda _: self.__converter_files_repository.acleanup(f"{user_id}/editor"))
#         .map(lambda _: self.__logger.info(f"Data for User '{user_id}' have been removed", depth=5))
#         .to_unit(),
#     )

# @as_awaitable_result
# async def __ais_expired(self) -> ContextResult[bool]:
#     try:
#         session_expiry_date = await sync_to_async(self.__request.session.get_expiry_date)()
#         return ContextResult[bool].success(timezone.now() > session_expiry_date)
#     except Exception as exception:
#         self.__logger.exception(exception, "Failed to check if session expired")
#         await self.__aclear()
#         return ContextResult[bool].failure(ErrorContext.server_error("Session is corrupted"))
