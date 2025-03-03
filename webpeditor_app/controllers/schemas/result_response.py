from http import HTTPStatus
from typing import Collection, Generic, Optional, TypeVar

from ninja import Schema
from pydantic import ConfigDict
from returns.io import IO
from returns.pipeline import is_successful
from types_linq import Enumerable

from webpeditor_app.core.extensions.result_extensions import FailureContext, ContextResult, IOContextResult

_TResponse = TypeVar("_TResponse")


class ResultResponse(Schema, Generic[_TResponse]):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    value: Optional[_TResponse] = None
    message: Optional[str] = None

    @classmethod
    def failure_500(cls, message: str) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return cls.failure(message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @classmethod
    def failure(cls, message: str, *, status_code: HTTPStatus) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return status_code, cls(message=message)

    @classmethod
    def from_results(
        cls,
        results: Collection[ContextResult[_TResponse]],
    ) -> tuple[HTTPStatus, "list[ResultResponse[_TResponse]]"]:
        if len(results) == 0:
            return HTTPStatus.NO_CONTENT, []

        results_enumerable = Enumerable([cls.from_result(result) for result in results])
        responses = results_enumerable.select(lambda response: response[1]).to_list()
        first_error_or_ok_status = (
            results_enumerable.where(
                lambda result_response: result_response[0].is_server_error or result_response[0].is_client_error
            )
            .select(lambda result_response: result_response[0])
            .first2(HTTPStatus.OK)
        )

        return first_error_or_ok_status, list(responses)

    @classmethod
    def from_io_results(
        cls,
        results: Collection[IOContextResult[_TResponse]],
    ) -> tuple[HTTPStatus, list["ResultResponse[_TResponse]"]]:
        if len(results) == 0:
            return HTTPStatus.NO_CONTENT, []

        io_value_enumerable = Enumerable([cls.from_io_result(result) for result in results])
        io_responses = io_value_enumerable.select(lambda response: response.map(lambda r: r[1])._inner_value).to_list()
        first_error_or_ok_status = (
            io_value_enumerable.where(
                lambda io_value: io_value.map(lambda r: r[0].is_server_error or r[0].is_client_error)._inner_value
            )
            .select(lambda io_value: io_value.map(lambda r: r[0])._inner_value)
            .first2(HTTPStatus.OK)
        )

        return first_error_or_ok_status, list(io_responses)

    @classmethod
    def from_result(cls, result: ContextResult[_TResponse]) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        if not is_successful(result):
            return cls.from_failure(result.failure())
        return cls.from_value(result.unwrap())

    @classmethod
    def from_io_result(cls, result: IOContextResult[_TResponse]) -> IO[tuple[HTTPStatus, "ResultResponse[_TResponse]"]]:
        if not is_successful(result):
            return cls.from_io_failure(result.failure())
        return cls.from_io_value(result.unwrap())

    @classmethod
    def from_value(cls, value: _TResponse) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return HTTPStatus.OK, cls(value=value)

    @classmethod
    def from_io_value(cls, io_value: IO[_TResponse]) -> IO[tuple[HTTPStatus, "ResultResponse[_TResponse]"]]:
        return io_value.map(lambda value: (HTTPStatus.OK, cls(value=value)))

    @classmethod
    def from_failure(cls, failure: FailureContext) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return cls.__map_status_code(failure.error_code), cls(message=failure.message)

    @classmethod
    def from_io_failure(cls, io_failure: IO[FailureContext]) -> IO[tuple[HTTPStatus, "ResultResponse[_TResponse]"]]:
        return io_failure.map(lambda failure: (cls.__map_status_code(failure.error_code), cls(message=failure.message)))

    @classmethod
    def empty(cls) -> tuple[HTTPStatus, "ResultResponse[_TResponse]"]:
        return HTTPStatus.NO_CONTENT, cls()

    @classmethod
    def __map_status_code(cls, error_code: FailureContext.ErrorCode) -> HTTPStatus:
        match error_code:
            case FailureContext.ErrorCode.BAD_REQUEST:
                return HTTPStatus.BAD_REQUEST
            case FailureContext.ErrorCode.UNAUTHORIZED:
                return HTTPStatus.UNAUTHORIZED
            case FailureContext.ErrorCode.FORBIDDEN:
                return HTTPStatus.FORBIDDEN
            case FailureContext.ErrorCode.NOT_FOUND:
                return HTTPStatus.NOT_FOUND
            case _:
                return HTTPStatus.INTERNAL_SERVER_ERROR
