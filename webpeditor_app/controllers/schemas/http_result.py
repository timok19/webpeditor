from http import HTTPStatus
from typing import Optional, final

from ninja import Schema, Field
from pydantic import ConfigDict

from webpeditor_app.core.context_result import ErrorContext, ContextResult, EnumerableContextResult

type HTTPResultWithStatus[T: Schema] = tuple[HTTPStatus, HTTPResult[T]]
type HTTPResultListWithStatus[T: Schema] = tuple[HTTPStatus, list[HTTPResult[T]]]


@final
class HTTPResult[T: Schema](Schema):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    value: Optional[T] = None
    message: str = Field(default_factory=str)
    reasons: list[str] = Field(default_factory=list[str])

    @classmethod
    def failure_500(cls, message: str) -> HTTPResultWithStatus[T]:
        return cls.failure(message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @classmethod
    def failure(cls, message: str, *, status_code: HTTPStatus) -> HTTPResultWithStatus[T]:
        return status_code, cls(message=message)

    @classmethod
    def from_results(cls, results: EnumerableContextResult[T]) -> HTTPResultListWithStatus[T]:
        if results.count() == 0:
            return HTTPStatus.NO_CONTENT, []

        res = results.select(cls.from_result)
        http_status = res.select(lambda r: r[0]).first2(lambda s: s.is_server_error or s.is_client_error, HTTPStatus.OK)
        http_results = res.select(lambda r: r[1]).to_list()

        return http_status, http_results

    @classmethod
    def from_result(cls, result: ContextResult[T]) -> HTTPResultWithStatus[T]:
        return cls.from_error(result.error) if result.is_error() else cls.from_value(result.ok)

    @classmethod
    def from_value(cls, value: T) -> HTTPResultWithStatus[T]:
        return HTTPStatus.OK, cls(value=value)

    @classmethod
    def from_error(cls, error: ErrorContext) -> HTTPResultWithStatus[T]:
        return cls.__map_status_code(error.error_code), cls(message=error.message, reasons=error.reasons)

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
