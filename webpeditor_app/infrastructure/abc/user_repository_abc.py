from abc import ABC, abstractmethod

from webpeditor_app.core.context_result import AwaitableContextResult
from webpeditor_app.models.app_user import AppUser


class UserRepositoryABC(ABC):
    @abstractmethod
    def get_user_async(self, user_id: str) -> AwaitableContextResult[AppUser]: ...
