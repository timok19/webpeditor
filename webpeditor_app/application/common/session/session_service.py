from datetime import datetime
from typing import Any, Final, final, Optional

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.db import SessionStore
from django.http.request import HttpRequest
from django.utils import timezone
from expression import Option
from names_generator import generate_name
from uuid_utils import uuid7

from webpeditor import settings
from webpeditor_app.application.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, as_awaitable_result, ErrorContext


@final
class SessionService:
    __USER_ID_KEY: Final[str] = "USER_ID"
    __SESSION_EXPIRY_SET_KEY: Final[str] = "SESSION_EXPIRY_SET"

    def __init__(
        self,
        http_request: HttpRequest,
        user_service: UserServiceABC,
        logger: LoggerABC,
    ) -> None:
        self.__http_request: Final[HttpRequest] = http_request
        self.__user_service: Final[UserServiceABC] = user_service
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aget_user_id(self) -> ContextResult[str]:
        return await self.__aget_user_id() if not await self.__ais_expired() else await self.__acreate_user_id()

    @as_awaitable_result
    async def __acreate_user_id(self) -> ContextResult[str]:
        user_id = self.__generate_id()
        signed_user_id = self.__user_service.sign_id(user_id)
        await self.__aset(self.__USER_ID_KEY, signed_user_id)
        return await self.__aget_user_id()

    @as_awaitable_result
    async def __aget_user_id(self) -> ContextResult[str]:
        return await (
            ContextResult[str]
            .from_result(
                Option.of_optional(await self.__aget(self.__USER_ID_KEY))
                .to_result(ErrorContext.not_found(f"Unable to find User in the {SessionStore.__name__}!"))
                .bind(self.__user_service.unsign_id)
            )
            .amap(self.__arefresh_expiry)
        )

    async def __arefresh_expiry(self, user_id: str) -> str:
        await self.__aset_expiry(settings.SESSION_COOKIE_AGE)

        expire_at = await self.__aget_expiry_date()
        self.__logger.debug(f"Session for User '{user_id}' will expire at {expire_at.time()} UTC.")

        await self.__aset(self.__SESSION_EXPIRY_SET_KEY, True)
        return user_id

    async def __ais_expired(self) -> bool:
        is_expiry_set = await self.__aget(self.__SESSION_EXPIRY_SET_KEY)
        expire_at = await self.__aget_expiry_date()
        return not is_expiry_set or timezone.now() > expire_at

    async def __aget(self, key: str) -> Optional[Any]:
        return await sync_to_async(self.__http_request.session.get)(key)

    async def __aset(self, key: str, value: Any) -> None:
        await sync_to_async(self.__http_request.session.__setitem__)(key, value)
        return await sync_to_async(self.__http_request.session.save)()

    async def __aget_expiry_date(self) -> datetime:
        return await sync_to_async(self.__http_request.session.get_expiry_date)()

    async def __aset_expiry(self, value: int) -> None:
        return await sync_to_async(self.__http_request.session.set_expiry)(value)

    @staticmethod
    def __generate_id() -> str:
        return f"{generate_name(style='hyphen')}-{uuid7()}"
