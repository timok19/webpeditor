from abc import ABC, abstractmethod

from ninja import Field, Schema

from webpeditor_app.core.extensions.result_extensions import FailureContext, ContextResult, ResultExtensions


class ValidationResult(Schema):
    errors: list[str] = Field(default_factory=list[str])

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def is_successful(self) -> bool:
        return not any(self.errors)

    def as_context_result(self) -> ContextResult[None]:
        if not self.is_successful():
            error_message = f"Validation failed. Reasons: [{', '.join(self.errors)}]"
            return ResultExtensions.failure(FailureContext.ErrorCode.BAD_REQUEST, error_message)
        return ResultExtensions.success(None)


class ValidatorABC[TModel: object](ABC):
    @abstractmethod
    def validate(self, value: TModel) -> ValidationResult: ...
