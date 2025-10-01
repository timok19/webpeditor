from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field

from webpeditor_app.core.result import ContextResult, ErrorContext


class ValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    errors: list[str] = Field(default_factory=list[str])

    def to_result(self) -> ContextResult[None]:
        return (
            ContextResult.empty_failure(ErrorContext.bad_request("Request is invalid", self.errors))
            if any(self.errors)
            else ContextResult.empty_success()
        )


class ValidatorABC[TValue](ABC):
    @abstractmethod
    def validate(self, value: TValue) -> ValidationResult: ...
