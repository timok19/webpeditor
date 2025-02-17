from abc import ABC, abstractmethod
from typing import Optional

from types_linq import Enumerable


class ValidationResult(Enumerable[str]):
    def __init__(self) -> None:
        super().__init__([])

    @property
    def errors(self) -> list[str]:
        return self.to_list()

    @property
    def message(self) -> Optional[str]:
        return f"Validation failed. Errors: [{', '.join(self.errors)}]" if self.any() else None

    def add_error(self, message: str) -> "ValidationResult":
        self.append(message)
        return self

    def is_successful(self) -> bool:
        return not self.any()


class ValidatorABC[TModel: object](ABC):
    @abstractmethod
    def validate(self, value: TModel) -> ValidationResult: ...
