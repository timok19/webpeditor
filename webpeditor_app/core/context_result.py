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

    @classmethod
    def bad_request(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.__create(cls.ErrorCode.BAD_REQUEST, message, reasons)

    @classmethod
    def unauthorized(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.__create(cls.ErrorCode.UNAUTHORIZED, message, reasons)

    @classmethod
    def forbidden(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.__create(cls.ErrorCode.FORBIDDEN, message, reasons)

    @classmethod
    def not_found(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.__create(cls.ErrorCode.NOT_FOUND, message, reasons)

    @classmethod
    def server_error(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.__create(cls.ErrorCode.INTERNAL_SERVER_ERROR, message, reasons)

    def to_str(self):
        return f"Error code: {self.error_code}, Message: {self.message}, Reasons: [{self.reasons if any(self.reasons) else ''}]"

    @classmethod
    def __create(
        cls,
        error_code: ErrorCode,
        message: Optional[str] = None,
        reasons: Optional[list[str]] = None,
    ) -> "ErrorContext":
        return cls(error_code=error_code, message=message or "", reasons=reasons or [])


class ContextResult[TOut](Result[TOut, ErrorContext]):
    @staticmethod
    def success(value: TOut) -> "ContextResult[TOut]":
        return ContextResult(tag="ok", ok=value)

    @staticmethod
    def failure(error: ErrorContext) -> "ContextResult[TOut]":
        return ContextResult[TOut].failure2(error.error_code, error.message, error.reasons)

    @staticmethod
    def failure2(
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
                return cls.success(value)
            case Result(tag="error", error=error):
                return cls.failure(error)
            case _:
                return cls.unexpected_result()

    def match(
        self,
        success_func: Callable[[TOut], TOut],
        error_func: Callable[[ErrorContext], ErrorContext],
    ) -> "ContextResult[TOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return self.success(success_func(value))
            case ContextResult(tag="error", error=error):
                return self.failure(error_func(error))
            case _:
                return self.unexpected_result()

    @override
    def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    async def map_async[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    @override
    def bind[TNewOut](self, mapper: Callable[[TOut], Result[TNewOut, ErrorContext]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    def bind2[TNewOut](self, mapper: Callable[[TOut], "ContextResult[TNewOut]"]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
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
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected_result()

    @staticmethod
    def unexpected_result() -> "ContextResult[TOut]":
        return ContextResult[TOut].failure(ErrorContext.server_error("Unexpected result"))


class EnumerableContextResult[TOut](Enumerable[ContextResult[TOut]]):
    @staticmethod
    def from_results(*results: ContextResult[TOut]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def match(
        self,
        success_func: Callable[[Enumerable[TOut]], Enumerable[TOut]],
        error_func: Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]],
    ) -> "EnumerableContextResult[TOut]":
        return (
            EnumerableContextResult(
                error_func(self.where(lambda r: r.is_error()).select(lambda r: r.error)).select(
                    ContextResult[TOut].failure
                )
            )
            if self.any(lambda result: result.is_error())
            else EnumerableContextResult(
                success_func(self.where(lambda r: r.is_ok()).select(lambda r: r.ok)).select(ContextResult[TOut].success)
            )
        )
