from http import HTTPStatus
from typing import Generic, Optional, TypeVar, final

from ninja import Schema, Field
from pydantic import ConfigDict

from webpeditor_app.core.context_result import ErrorContext, ContextResult, MultipleContextResults

_TResponse = TypeVar("_TResponse")


@final
class ResultResponse(Schema, Generic[_TResponse]):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    value: Optional[_TResponse] = None
    message: str = Field(default_factory=str)
    reasons: list[str] = Field(default_factory=list[str])

    @classmethod
    def failure_500(cls, message: str) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return cls.failure(message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @classmethod
    def failure(cls, message: str, *, status_code: HTTPStatus) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return status_code, cls(message=message)

    @classmethod
    def from_multiple_results(
        cls,
        results: MultipleContextResults[_TResponse],
    ) -> tuple[HTTPStatus, "list[ResultResponse[_TResponse]]"]:
        if results.count() == 0:
            return HTTPStatus.NO_CONTENT, []

        responses = results.select(lambda result: cls.from_result(result))

        result_responses = responses.select(lambda response: response[1]).to_list()
        http_status = responses.select(lambda response: response[0]).first2(
            lambda status_code: status_code.is_server_error or status_code.is_client_error,
            HTTPStatus.OK,
        )

        return http_status, result_responses

    @classmethod
    def from_result(cls, result: ContextResult[_TResponse]) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return cls.from_error(result.error) if result.is_error() else cls.from_value(result.ok)

    @classmethod
    def from_value(cls, value: _TResponse) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return HTTPStatus.OK, cls(value=value)

    @classmethod
    def from_error(cls, error: ErrorContext) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return cls.__map_status_code(error.error_code), cls(message=error.message, reasons=error.reasons)

    @classmethod
    def no_content(cls) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
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
