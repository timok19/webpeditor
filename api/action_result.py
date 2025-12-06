from http import HTTPStatus
from typing import Optional, Self, Union, final

from ninja import Field, Schema
from pydantic import ConfigDict

from core.result import ContextResult, EnumerableContextResult, ErrorContext

type ActionResultWithStatus[T: Schema] = tuple[HTTPStatus, ActionResult[T]]


@final
class ActionResult[T: Schema](Schema):
    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    ok: Optional[Union[T, list[T]]] = None
    error: Optional[Union["ActionResult.Error", list["ActionResult.Error"]]] = None

    @final
    class Error(Schema):
        model_config = ConfigDict(frozen=True)

        message: str = Field(default_factory=str)
        reasons: list[str] = Field(default_factory=list[str])

        @classmethod
        def create(cls, message: str, reasons: Optional[list[str]] = None) -> Self:
            return cls(message=message, reasons=reasons if reasons is not None else [])

    @classmethod
    def from_result(cls, result: ContextResult[T]) -> ActionResultWithStatus[T]:
        return (
            cls.__response(HTTPStatus.OK, cls(ok=result.ok))
            if result.is_ok()
            else cls.__response(
                cls.__map_status_code(result.error.error_code),
                cls(error=ActionResult.Error.create(result.error.message, result.error.reasons)),
            )
        )

    @classmethod
    def from_results(cls, results: EnumerableContextResult[T]) -> ActionResultWithStatus[T]:
        cached_results = results.as_cached()
        errors = cached_results.where(lambda result: result.is_error()).select(lambda result: result.error).order_by(lambda e: e.error_code)
        error_code = errors.select(lambda error: error.error_code).first2(None)
        action_errors = errors.select(lambda error: ActionResult.Error.create(error.message, error.reasons)).to_list()
        return (
            cls.__response(cls.__map_status_code(error_code), cls(error=action_errors))
            if error_code is not None
            else cls.__response(HTTPStatus.OK, cls(ok=cached_results.select(lambda result: result.ok).to_list()))
        )

    @classmethod
    def __map_status_code(cls, error_code: ErrorContext.ErrorCode) -> HTTPStatus:
        match error_code:
            case ErrorContext.ErrorCode.BAD_REQUEST:
                return HTTPStatus.BAD_REQUEST
            case ErrorContext.ErrorCode.UNAUTHORIZED:
                return HTTPStatus.UNAUTHORIZED
            case ErrorContext.ErrorCode.FORBIDDEN:
                return HTTPStatus.FORBIDDEN
            case ErrorContext.ErrorCode.NOT_FOUND:
                return HTTPStatus.NOT_FOUND
            case ErrorContext.ErrorCode.UNPROCESSABLE_ENTITY:
                return HTTPStatus.UNPROCESSABLE_ENTITY
            case _:
                return HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def __response(status_code: HTTPStatus, result: "ActionResult[T]") -> ActionResultWithStatus[T]:
        return status_code, result
