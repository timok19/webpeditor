from http import HTTPStatus
from typing import final

from ninja import Schema, Field
from pydantic import ConfigDict

from webpeditor_app.core.result import EnumerableContextResult, ErrorContext

type HTTPResultWithStatus[T: Schema] = tuple[HTTPStatus, HTTPResult[T]]


@final
class HTTPResult[T: Schema](Schema):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    values: list[T] = Field(default_factory=list[T])
    errors: list["HTTPResult.HTTPError"] = Field(default_factory=list["HTTPResult.HTTPError"])

    @final
    class HTTPError(Schema):
        model_config = ConfigDict(frozen=True)

        message: str
        reasons: list[str] = Field(default_factory=list[str])

    @classmethod
    def failure_500(cls, message: str) -> HTTPResultWithStatus[T]:
        return cls.failure(message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @classmethod
    def failure(cls, message: str, *, status_code: HTTPStatus) -> HTTPResultWithStatus[T]:
        return status_code, cls(errors=[HTTPResult.HTTPError(message=message)])

    @classmethod
    def from_results(cls, results: EnumerableContextResult[T]) -> HTTPResultWithStatus[T]:
        if results.count() == 0:
            return cls.no_content()

        if results.any(lambda result: result.is_error()):
            errors = results.where(lambda result: result.is_error()).select(lambda result: result.error)
            error_code = errors.select(lambda result: result.error_code).first()
            http_errors = errors.select(lambda e: HTTPResult.HTTPError(message=e.message, reasons=e.reasons)).to_list()
            return cls.__map_status_code(error_code), cls(errors=http_errors)

        values = results.select(lambda result: result.ok).to_list()
        return HTTPStatus.OK, cls(values=values)

    @classmethod
    def no_content(cls) -> HTTPResultWithStatus[T]:
        return HTTPStatus.NO_CONTENT, cls()

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
            case _:
                return HTTPStatus.INTERNAL_SERVER_ERROR
