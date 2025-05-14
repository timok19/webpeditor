from abc import ABC, abstractmethod
from datetime import datetime

from webpeditor_app.core.context_result import AwaitableContextResult
from webpeditor_app.models.app_user import AppUser


class UserRepositoryABC(ABC):
    @abstractmethod
    def acreate_user(
        self,
        session_key: str,
        session_key_expiration_date: datetime,
    ) -> AwaitableContextResult[AppUser]: ...

    @abstractmethod
    def aget_user(self, user_id: str) -> AwaitableContextResult[AppUser]: ...
