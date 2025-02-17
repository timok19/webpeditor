from abc import ABC, abstractmethod
from typing import Optional


class ValidationResult:
    def __init__(self) -> None:
        self.__errors: list[str] = []

    @property
    def message(self) -> Optional[str]:
        return f"Validation failed. Errors: [{', '.join(self.__errors)}]" if len(self.__errors) > 0 else None

    @property
    def errors(self) -> list[str]:
        return self.__errors

    def add_error(self, message: str) -> None:
        self.__errors.append(message)

    def is_successful(self) -> bool:
        return len(self.__errors) == 0


class ValidatorABC[TModel: object](ABC):
    @abstractmethod
    def validate(self, value: TModel) -> ValidationResult: ...
