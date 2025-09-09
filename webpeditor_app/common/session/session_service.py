from datetime import timedelta, datetime
from typing import Any, ClassVar, Final, Union, final, Optional

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.db import SessionStore
from django.http.request import HttpRequest
from django.utils import timezone
from expression import Option
from names_generator import generate_name
from uuid_utils import uuid7

from webpeditor_app.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, as_awaitable_result, ErrorContext


@final
class SessionService:
    __user_id_key: ClassVar[str] = "USER_ID"
    __expire_at_key: ClassVar[str] = "EXPIRE_AT"
    __session_lifetime_in_seconds: ClassVar[int] = 15 * 60

    def __init__(
        self,
        request: HttpRequest,
        user_service: UserServiceABC,
        logger: LoggerABC,
    ) -> None:
        self.__request: Final[HttpRequest] = request
        self.__user_service: Final[UserServiceABC] = user_service
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def asynchronize(self) -> ContextResult[str]:
        return await self.__aget_user_id() if not await self.__ais_expired() else await self.__acreate_user_id()

    @as_awaitable_result
    async def __acreate_user_id(self) -> ContextResult[str]:
        user_id = self.__generate_id()
        signed_user_id = self.__user_service.sign_id(user_id)
        await self.__aset_item(self.__user_id_key, signed_user_id)
        return await self.__aget_user_id()

    @as_awaitable_result
    async def __aget_user_id(self) -> ContextResult[str]:
        return await (
            ContextResult[str]
            .from_result(
                Option.of_optional(await self.__aget_item(self.__user_id_key))
                .to_result(ErrorContext.not_found(f"Unable to find User in the {SessionStore.__name__}!"))
                .bind(self.__user_service.unsign_id)
            )
            .amap1(self.__arefresh_expiry(), lambda user_id, _: user_id)
        )

    async def __arefresh_expiry(self) -> None:
        expire_at = timezone.now() + timedelta(seconds=self.__session_lifetime_in_seconds)
        await self.__aset_item(self.__expire_at_key, expire_at.timestamp())
        await self.__aset_expiry(self.__session_lifetime_in_seconds)
        return None

    async def __aset_expiry(self, value: Optional[Union[datetime, int]]) -> None:
        await sync_to_async(self.__request.session.set_expiry)(value)
        await sync_to_async(self.__request.session.save)()
        return None

    async def __ais_expired(self) -> bool:
        expire_at = await self.__aget_item(self.__expire_at_key)
        return not expire_at or timezone.now().timestamp() > expire_at

    async def __aget_item(self, key: str) -> Optional[Any]:
        return await sync_to_async(self.__request.session.get)(key)

    async def __aset_item(self, key: str, value: Any) -> None:
        await sync_to_async(self.__request.session.__setitem__)(key, value)
        await sync_to_async(self.__request.session.save)()
        return None

    @staticmethod
    def __generate_id() -> str:
        return f"{generate_name(style='hyphen')}-{uuid7()}"
