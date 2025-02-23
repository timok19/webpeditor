from abc import ABC, abstractmethod

from ninja import Field, Schema

from webpeditor_app.core.extensions.result_extensions import FailureContext, ResultOfType, ResultExtensions


class ValidationResult(Schema):
    errors: list[str] = Field(default_factory=list[str])

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def is_successful(self) -> bool:
        return not any(self.errors)

    def as_based_result(self) -> ResultOfType[None]:
        return (
            ResultExtensions.failure(
                FailureContext.ErrorCode.BAD_REQUEST,
                f"Validation failed. Errors: [{', '.join(self.errors)}]" if any(self.errors) else None,
            )
            if not self.is_successful()
            else ResultExtensions.success(None)
        )


class ValidatorABC[TModel: object](ABC):
    @abstractmethod
    def validate(self, value: TModel) -> ValidationResult: ...
