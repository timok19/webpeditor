from enum import IntEnum, auto
from typing import Awaitable, Collection, Optional, Callable, override, Any, Generator

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
        return cls.create(cls.ErrorCode.BAD_REQUEST, message, reasons)

    @classmethod
    def unauthorized(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.UNAUTHORIZED, message, reasons)

    @classmethod
    def forbidden(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.FORBIDDEN, message, reasons)

    @classmethod
    def not_found(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.NOT_FOUND, message, reasons)

    @classmethod
    def server_error(cls, message: Optional[str] = None, reasons: Optional[list[str]] = None) -> "ErrorContext":
        return cls.create(cls.ErrorCode.INTERNAL_SERVER_ERROR, message, reasons)

    @classmethod
    def create(
        cls,
        error_code: ErrorCode,
        message: Optional[str] = None,
        reasons: Optional[list[str]] = None,
    ) -> "ErrorContext":
        return cls(error_code=error_code, message=message or "", reasons=reasons or [])

    def to_str(self) -> str:
        return f"Error code: {self.error_code}, Message: {self.message}, Reasons: [{self.reasons if any(self.reasons) else ''}]"


class ContextResult[TOut](Result[TOut, ErrorContext]):
    @staticmethod
    def success(value: TOut) -> "ContextResult[TOut]":
        return ContextResult(tag="ok", ok=value)

    @staticmethod
    def failure(error: ErrorContext) -> "ContextResult[TOut]":
        return ContextResult[TOut].failure2(error.error_code, error.message, error.reasons)

    @staticmethod
    def failures(*errors: ErrorContext) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut]([ContextResult[TOut].failure(error) for error in errors])

    @staticmethod
    def failure2(
        error_code: ErrorContext.ErrorCode,
        message: Optional[str] = None,
        reasons: Optional[list[str]] = None,
    ) -> "ContextResult[TOut]":
        error = ErrorContext(error_code=error_code, message=message or "", reasons=reasons or [])
        return ContextResult(tag="error", error=error)

    @classmethod
    def from_result(cls, result: Result[TOut, ErrorContext]) -> "ContextResult[TOut]":
        match result:
            case Result(tag="ok", ok=value):
                return cls.success(value)
            case Result(tag="error", error=error):
                return cls.failure(error)
            case _:
                return cls.unexpected()

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
                return self.unexpected()

    @override
    def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    @override
    def bind[TNewOut](self, mapper: Callable[[TOut], Result[TNewOut, ErrorContext]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    def bind2[TNewOut](self, mapper: Callable[[TOut], "ContextResult[TNewOut]"]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                return ContextResult[TNewOut].unexpected()

    def bind_async[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
    ) -> "AwaitableContextResult[TNewOut]":
        async def bind_async() -> ContextResult[TNewOut]:
            match self:
                case ContextResult(tag="ok", ok=value):
                    return ContextResult[TNewOut].from_result(await mapper(value))
                case ContextResult(tag="error", error=error):
                    return ContextResult[TNewOut].failure(error)
                case _:
                    return ContextResult[TNewOut].unexpected()

        return AwaitableContextResult(bind_async())

    def map_async[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "AwaitableContextResult[TNewOut]":
        async def map_async() -> ContextResult[TNewOut]:
            match self:
                case ContextResult(tag="ok", ok=value):
                    return ContextResult[TNewOut].success(await mapper(value))
                case ContextResult(tag="error", error=error):
                    return ContextResult[TNewOut].failure(error)
                case _:
                    return ContextResult[TNewOut].unexpected()

        return AwaitableContextResult(map_async())

    def bind_many_async[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "AwaitableEnumerableContextResult[TNewOut]":
        async def bind_many_async() -> EnumerableContextResult[TNewOut]:
            match self:
                case ContextResult(tag="ok", ok=value):
                    return await mapper(value)
                case ContextResult(tag="error", error=error):
                    return ContextResult[TNewOut].failures(error)
                case _:
                    return ContextResult[TNewOut].unexpected_many()

        return AwaitableEnumerableContextResult(bind_many_async())

    @staticmethod
    def unexpected() -> "ContextResult[TOut]":
        return ContextResult[TOut].failure(ErrorContext.server_error("Unexpected error"))

    @staticmethod
    def unexpected_many() -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut]([ContextResult[TOut].unexpected()])


class AwaitableContextResult[TOut](Awaitable[ContextResult[TOut]]):
    def __init__(self, awaitable: Awaitable[ContextResult[TOut]]) -> None:
        self.__awaitable_result: Awaitable[ContextResult[TOut]] = awaitable

    def __await__(self) -> Generator[Any, Any, ContextResult[TOut]]:
        return self.__awaitable_result.__await__()

    def bind_async[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]],
    ) -> "AwaitableContextResult[TNewOut]":
        async def bind_async() -> ContextResult[TNewOut]:
            return await (await self.__awaitable_result).bind_async(mapper)

        return AwaitableContextResult(bind_async())

    def map_async[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable[TNewOut]],
    ) -> "AwaitableContextResult[TNewOut]":
        async def map_async() -> ContextResult[TNewOut]:
            return await (await self.__awaitable_result).map_async(mapper)

        return AwaitableContextResult(map_async())

    def bind_many_async[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "AwaitableEnumerableContextResult[TNewOut]":
        async def bind_many_async() -> EnumerableContextResult[TNewOut]:
            return await (await self.__awaitable_result).bind_many_async(mapper)

        return AwaitableEnumerableContextResult(bind_many_async())

    def bind[TNewOut](self, mapper: Callable[[TOut], ContextResult[TNewOut]]) -> "AwaitableContextResult[TNewOut]":
        async def bind_async() -> ContextResult[TNewOut]:
            return (await self.__awaitable_result).bind(mapper)

        return AwaitableContextResult(bind_async())

    def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "AwaitableContextResult[TNewOut]":
        async def map_async() -> ContextResult[TNewOut]:
            return (await self.__awaitable_result).map(mapper)

        return AwaitableContextResult(map_async())


class EnumerableContextResult[TOut](Enumerable[ContextResult[TOut]]):
    @staticmethod
    def from_results(results: Collection[ContextResult[TOut]]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def match(
        self,
        success_func: Callable[[Enumerable[TOut]], Enumerable[TOut]],
        error_func: Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]],
    ) -> "EnumerableContextResult[TOut]":
        if self.any(lambda result: result.is_error()):
            errors = self.where(lambda result: result.is_error()).select(lambda result: result.error)
            return EnumerableContextResult(error_func(errors).select(ContextResult[TOut].failure))

        values = self.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        return EnumerableContextResult(success_func(values).select(ContextResult[TOut].success))


class AwaitableEnumerableContextResult[TOut](Awaitable[EnumerableContextResult[TOut]]):
    def __init__(self, awaitable: Awaitable[EnumerableContextResult[TOut]]) -> None:
        self.__awaitable_result: Awaitable[EnumerableContextResult[TOut]] = awaitable

    def __await__(self) -> Generator[Any, Any, EnumerableContextResult[TOut]]:
        return self.__awaitable_result.__await__()

    def match(
        self,
        success_func: Callable[[Enumerable[TOut]], Enumerable[TOut]],
        error_func: Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]],
    ) -> "AwaitableEnumerableContextResult[TOut]":
        async def match_async() -> EnumerableContextResult[TOut]:
            return (await self.__awaitable_result).match(success_func, error_func)

        return AwaitableEnumerableContextResult(match_async())
