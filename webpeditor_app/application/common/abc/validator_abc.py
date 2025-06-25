from abc import ABC, abstractmethod

from ninja import Schema
from pydantic import ConfigDict, Field

from webpeditor_app.core.result import ContextResult, ErrorContext
from webpeditor_app.globals import Unit


class ValidationResult(Schema):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    errors: list[str] = Field(default_factory=list[str])

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def to_context_result(self) -> ContextResult[Unit]:
        return (
            ContextResult[Unit].failure(ErrorContext.bad_request("Request is invalid", self.errors))
            if any(self.errors)
            else ContextResult[Unit].success(Unit())
        )


class ValidatorABC[TValue](ABC):
    @abstractmethod
    def validate(self, value: TValue) -> ValidationResult: ...
