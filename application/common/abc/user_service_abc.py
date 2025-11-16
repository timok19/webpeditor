from abc import ABC, abstractmethod

from core.result import ContextResult


class UserServiceABC(ABC):
    @abstractmethod
    def sign_id(self, user_id: str) -> str: ...

    @abstractmethod
    def unsign_id(self, signed_user_id: str) -> ContextResult[str]: ...
