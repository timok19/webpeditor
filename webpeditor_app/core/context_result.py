from enum import IntEnum, auto
from typing import Awaitable, Optional, Callable, override

from expression import Result
from ninja import Field, Schema
from pydantic import ConfigDict
from types_linq import Enumerable


class ErrorContext(Schema):
    class ErrorCode(IntEnum):
        BAD_REQUEST = auto()
        UNAUTHORIZED = auto()
        FORBIDDEN = auto()
        NOT_FOUND = auto()
        INTERNAL_SERVER_ERROR = auto()

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    error_code: ErrorCode
    message: str = Field(default_factory=str)
    reasons: list[str] = Field(default_factory=list[str])

    def to_str(self):
        return f"Error code: {self.error_code}, Message: {self.message}, Reasons: [{self.reasons if any(self.reasons) else ''}]"


type ContextResultType[TOut] = Result[TOut, ErrorContext]


class ContextResult[TOut](Result[TOut, ErrorContext]):
    @staticmethod
    @override
    def Ok(value: TOut) -> "ContextResult[TOut]":
        return ContextResult(tag="ok", ok=value)

    @staticmethod
    @override
    def Error(error: ErrorContext) -> "ContextResult[TOut]":
        return ContextResult[TOut].Error2(error.error_code, error.message, error.reasons)

    @staticmethod
    def Error2(
        error_code: ErrorContext.ErrorCode,
        message: Optional[str] = None,
        reasons: Optional[list[str]] = None,
    ) -> "ContextResult[TOut]":
        return ContextResult(
            tag="error",
            error=ErrorContext(
                error_code=error_code,
                message=message or "",
                reasons=reasons or [],
            ),
        )

    @classmethod
    def from_result(cls, result: Result[TOut, ErrorContext]) -> "ContextResult[TOut]":
        match result:
            case Result(tag="ok", ok=value):
                return cls.Ok(value)
            case Result(tag="error", error=error):
                return cls.Error(error)
            case _:
                return cls.unexpected_result()

    def match(
        self,
        success_func: Callable[[TOut], TOut],
        error_func: Callable[[ErrorContext], ErrorContext],
    ) -> "ContextResult[TOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return self.Ok(success_func(value))
            case ContextResult(tag="error", error=error):
                return self.Error(error_func(error))
            case _:
                return self.unexpected_result()

    @override
    def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].Ok(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].Error(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    async def map_async[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].Ok(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].Error(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    @override
    def bind[TNewOut](self, mapper: Callable[[TOut], ContextResultType[TNewOut]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].Error(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    async def bind_async[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].Error(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    @staticmethod
    def unexpected_result() -> "ContextResult[TOut]":
        return ContextResult[TOut].Error2(ErrorContext.ErrorCode.INTERNAL_SERVER_ERROR, "Unexpected result")


class MultipleContextResults[TOut](Enumerable[ContextResult[TOut]]):
    @staticmethod
    def from_results(*results: ContextResult[TOut]) -> "MultipleContextResults[TOut]":
        return MultipleContextResults[TOut](results)

    def match(
        self,
        success_func: Callable[[Enumerable[TOut]], Enumerable[TOut]],
        error_func: Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]],
    ) -> "MultipleContextResults[TOut]":
        if self.any(lambda result: result.is_error()):
            return MultipleContextResults(
                error_func(self.where(lambda r: r.is_error()).select(lambda r: r.error)).select(ContextResult.Error)
            )

        return MultipleContextResults(
            success_func(self.where(lambda r: r.is_ok()).select(lambda r: r.ok)).select(ContextResult.Ok)
        )
