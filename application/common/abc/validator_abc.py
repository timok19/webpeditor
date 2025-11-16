from abc import ABC, abstractmethod
from typing import Optional

from core.result import ContextResult


class ValidatorABC[T](ABC):
    @abstractmethod
    def validate(self, value: Optional[T]) -> ContextResult[T]: ...
