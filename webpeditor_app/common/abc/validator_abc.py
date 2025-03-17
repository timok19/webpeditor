from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from ninja import Schema
from pydantic import ConfigDict, Field

from webpeditor_app.core.context_result import ContextResult, ErrorContext

_TValue = TypeVar("_TValue")


class ValidationResult(Schema, Generic[_TValue]):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    value: _TValue
    errors: list[str] = Field(default_factory=list[str])

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def has_errors(self) -> bool:
        return any(self.errors)

    def to_context_result(self) -> ContextResult[_TValue]:
        return (
            ContextResult[_TValue].Error2(ErrorContext.ErrorCode.BAD_REQUEST, "Validation failed", self.errors)
            if self.has_errors()
            else ContextResult[_TValue].Ok(self.value)
        )


class ValidatorABC[TValue](ABC):
    @abstractmethod
    def validate(self, value: TValue) -> ValidationResult[TValue]: ...
