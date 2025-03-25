from abc import ABC, abstractmethod
from types import NoneType
from ninja import Schema
from pydantic import ConfigDict, Field

from webpeditor_app.core.context_result import ContextResult, ErrorContext


class ValidationResult(Schema):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    errors: list[str] = Field(default_factory=list[str])

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def has_errors(self) -> bool:
        return any(self.errors)

    def to_context_result(self) -> ContextResult[NoneType]:
        return (
            ContextResult[NoneType].Error(ErrorContext.bad_request("Validation failed", self.errors))
            if self.has_errors()
            else ContextResult[NoneType].Ok(None)
        )


class ValidatorABC[TValue](ABC):
    @abstractmethod
    def validate(self, value: TValue) -> ValidationResult: ...
