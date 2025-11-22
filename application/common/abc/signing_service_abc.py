from abc import ABC, abstractmethod

from core.result import ContextResult


class SigningServiceABC(ABC):
    @abstractmethod
    def sign(self, value: str) -> str: ...

    @abstractmethod
    def unsign(self, signed_value: str) -> ContextResult[str]: ...
