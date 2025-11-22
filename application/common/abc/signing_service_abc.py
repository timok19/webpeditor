from abc import ABC, abstractmethod
from typing import Any

from core.result import ContextResult


class SigningServiceABC(ABC):
    @abstractmethod
    def sign(self, value: Any) -> str: ...

    @abstractmethod
    def unsign(self, signed_value: str) -> ContextResult[str]: ...
