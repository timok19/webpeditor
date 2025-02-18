from abc import ABC, abstractmethod
from typing import Optional


class ValidationResult:
    def __init__(self) -> None:
        self.__errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return self.__errors

    @property
    def message(self) -> Optional[str]:
        return f"Validation failed. Errors: [{', '.join(self.__errors)}]" if any(self.__errors) else None

    def add_error(self, message: str) -> None:
        self.__errors.append(message)

    def is_successful(self) -> bool:
        return not any(self.__errors)


class ValidatorABC[TModel: object](ABC):
    @abstractmethod
    def validate(self, value: TModel) -> ValidationResult: ...
