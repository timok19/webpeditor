from abc import ABC, abstractmethod
from typing import Optional

from webpeditor_app.core.based_result import FailureContext, BasedResultOutput, BasedResult


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

    def as_based_result(self) -> BasedResultOutput[None]:
        return (
            BasedResult.failure(FailureContext.ErrorCode.BAD_REQUEST, self.message)
            if not self.is_successful()
            else BasedResult.success(None)
        )


class ValidatorABC[TModel: object](ABC):
    @abstractmethod
    def validate(self, value: TModel) -> ValidationResult: ...
