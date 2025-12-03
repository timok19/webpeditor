from abc import ABC, abstractmethod

from core.result import ContextResult


class ValidatorABC[T](ABC):
    @abstractmethod
    def validate(self, value: T) -> ContextResult[T]: ...
