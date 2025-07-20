from abc import ABC, abstractmethod
from datetime import datetime

from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.infrastructure.database.models import AppUser


class UserRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aget_or_create(
        self,
        session_key: str,
        session_key_expiration_date: datetime,
    ) -> ContextResult[AppUser]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget(self, user_id: str) -> ContextResult[AppUser]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_by_session_key(self, session_key: str) -> ContextResult[AppUser]: ...
