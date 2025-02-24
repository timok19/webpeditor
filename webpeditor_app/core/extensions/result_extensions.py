from enum import IntEnum, auto
from typing import Optional, Callable, Collection, overload

from pydantic import BaseModel, ConfigDict
from returns.pipeline import is_successful
from returns.result import Result, Failure, Success
from types_linq import Enumerable


class FailureContext(BaseModel):
    class ErrorCode(IntEnum):
        BAD_REQUEST = auto()
        UNAUTHORIZED = auto()
        FORBIDDEN = auto()
        NOT_FOUND = auto()
        INTERNAL_SERVER_ERROR = auto()

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    error_code: ErrorCode
    message: Optional[str] = None


type ContextResult[T] = Result[T, FailureContext]


class ResultExtensions[T]:
    @staticmethod
    def failure(error_code: FailureContext.ErrorCode, message: Optional[str] = None) -> ContextResult[T]:
        return Failure(FailureContext(error_code=error_code, message=message))

    @staticmethod
    def from_failure(failure: FailureContext) -> ContextResult[T]:
        return Failure(failure)

    @staticmethod
    def success(value: T) -> ContextResult[T]:
        return Success(value)

    @staticmethod
    def match(
        result: ContextResult[T],
        success_func: Callable[[T], ContextResult[T]],
        failure_func: Callable[[FailureContext], ContextResult[T]],
    ) -> ContextResult[T]:
        return failure_func(result.failure()) if not is_successful(result) else success_func(result.unwrap())

    @staticmethod
    def match_many(
        results: Collection[ContextResult[T]],
        success_func: Callable[[Enumerable[T]], Collection[ContextResult[T]]],
        failure_func: Callable[[Enumerable[FailureContext]], Collection[ContextResult[T]]],
    ) -> Collection[ContextResult[T]]:
        enum_results = Enumerable(results)
        errors = enum_results.where(lambda result: not is_successful(result)).select(lambda result: result.failure())
        successes = enum_results.where(is_successful).select(lambda result: result.unwrap())
        return failure_func(errors) if errors.any() else success_func(successes)
