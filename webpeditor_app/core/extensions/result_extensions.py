from enum import IntEnum, auto
from typing import Optional, Callable, Collection

from pydantic import BaseModel, ConfigDict
from returns.future import FutureResult, FutureSuccess, FutureFailure
from returns.io import IOResult, IO
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


type ContextResult[TValue] = Result[TValue, FailureContext]
type FutureContextResult[TValue] = FutureResult[TValue, FailureContext]
type IOContextResult[TValue] = IOResult[TValue, FailureContext]


class ResultExtensions:
    @classmethod
    def failure[TValue](
        cls, error_code: FailureContext.ErrorCode, message: Optional[str] = None
    ) -> ContextResult[TValue]:
        return Failure(FailureContext(error_code=error_code, message=message))

    @classmethod
    def future_failure[TValue](
        cls,
        error_code: FailureContext.ErrorCode,
        message: Optional[str] = None,
    ) -> FutureContextResult[TValue]:
        return FutureFailure(FailureContext(error_code=error_code, message=message))

    @classmethod
    def success[TValue](cls, value: TValue) -> ContextResult[TValue]:
        return Success(value)

    @classmethod
    def future_success[TValue](cls, value: TValue) -> FutureContextResult[TValue]:
        return FutureSuccess(value)

    @classmethod
    async def is_future_successful[TValue](cls, future_container: FutureContextResult[TValue]) -> bool:
        return is_successful(await future_container.awaitable())

    @classmethod
    def match[TValue](
        cls,
        result: ContextResult[TValue],
        success_func: Callable[[TValue], ContextResult[TValue]],
        failure_func: Callable[[FailureContext], ContextResult[TValue]],
    ) -> ContextResult[TValue]:
        return failure_func(result.failure()) if not is_successful(result) else success_func(result.unwrap())

    @classmethod
    async def match_future[TValue](
        cls,
        result: FutureContextResult[TValue],
        success_func: Callable[[IO[TValue]], FutureContextResult[TValue]],
        failure_func: Callable[[IO[FailureContext]], FutureContextResult[TValue]],
    ) -> FutureContextResult[TValue]:
        return (
            failure_func((await result.awaitable()).failure())
            if not await cls.is_future_successful(result)
            else success_func((await result.awaitable()).unwrap())
        )

    @classmethod
    def match_many[TValue](
        cls,
        results: Collection[ContextResult[TValue]],
        success_func: Callable[[Enumerable[TValue]], Collection[ContextResult[TValue]]],
        failure_func: Callable[[Enumerable[FailureContext]], Collection[ContextResult[TValue]]],
    ) -> Collection[ContextResult[TValue]]:
        errors = Enumerable([])
        successes = Enumerable([])

        for result in results:
            if not is_successful(result):
                errors.append(result.failure())
            else:
                successes.append(result.unwrap())

        return failure_func(errors) if errors.any() else success_func(successes)

    @classmethod
    async def match_many_futures[TValue](
        cls,
        results: Collection[FutureContextResult[TValue]],
        success_func: Callable[[Enumerable[IO[TValue]]], Collection[IOContextResult[TValue]]],
        failure_func: Callable[[Enumerable[IO[FailureContext]]], Collection[IOContextResult[TValue]]],
    ) -> Collection[IOContextResult[TValue]]:
        errors = Enumerable([])
        successes = Enumerable([])

        for result in results:
            if not await cls.is_future_successful(result):
                errors.append((await result.awaitable()).failure())
            else:
                successes.append((await result.awaitable()).unwrap())

        return failure_func(errors) if errors.any() else success_func(successes)
