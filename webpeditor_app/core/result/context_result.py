from typing import TYPE_CHECKING, Awaitable, Callable, override

from expression import Result
from types_linq import Enumerable

from webpeditor_app.core.result.decorators import as_awaitable_result, as_awaitable_enumerable_result
from webpeditor_app.core.result.error_context import ErrorContext
from webpeditor_app.globals import Unit

if TYPE_CHECKING:
    from webpeditor_app.core.result import EnumerableContextResult


class ContextResult[TOut](Result[TOut, ErrorContext]):
    @staticmethod
    def success(value: TOut) -> "ContextResult[TOut]":
        return ContextResult(tag="ok", ok=value)

    @classmethod
    @as_awaitable_result
    async def asuccess(cls, value: TOut) -> "ContextResult[TOut]":
        return cls.success(value)

    @staticmethod
    def failure(error: ErrorContext) -> "ContextResult[TOut]":
        return ContextResult(
            tag="error",
            error=ErrorContext(
                error_code=error.error_code,
                message=error.message or "",
                reasons=error.reasons or [],
            ),
        )

    @classmethod
    @as_awaitable_result
    async def afailure(cls, error: ErrorContext) -> "ContextResult[TOut]":
        return cls.failure(error)

    @classmethod
    def failures(cls, *errors: ErrorContext) -> "EnumerableContextResult[TOut]":
        from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult

        return EnumerableContextResult[TOut](Enumerable(errors).select(ContextResult[TOut].failure))

    @classmethod
    def from_result(cls, result: Result[TOut, ErrorContext]) -> "ContextResult[TOut]":
        match result:
            case Result(tag="ok", ok=value):
                return cls.success(value)
            case Result(tag="error", error=error):
                return cls.failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(result)}'")

    def log_result(
        self,
        log_success: Callable[[TOut], None] = lambda _: None,
        log_error: Callable[[ErrorContext], None] = lambda _: None,
    ) -> "ContextResult[TOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                log_success(value)
                return self.success(value)
            case ContextResult(tag="error", error=error):
                log_error(error)
                return self.failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @override
    def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @override
    def map2[TOutOther, TNewOut](
        self,
        other: Result[TOutOther, ErrorContext],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(other.map(lambda value_: mapper(value, value_)))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @as_awaitable_result
    async def amap[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @as_awaitable_result
    async def amap2[TOutOther, TNewOut](
        self,
        other: Awaitable["ContextResult[TOutOther]"],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        return self.map2(await other, mapper)

    @override
    def bind[TNewOut](self, mapper: Callable[[TOut], Result[TNewOut, ErrorContext]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @as_awaitable_result
    async def abind[TNewOut](self, mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]]) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].from_result(await mapper(value))
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @override
    def or_else(self, other: Result[TOut, ErrorContext]) -> "ContextResult[TOut]":
        return self if self.is_ok() else ContextResult[TOut].from_result(other)

    @as_awaitable_result
    async def aor_else(self, other: Awaitable["ContextResult[TOut]"]) -> "ContextResult[TOut]":
        return self if self.is_ok() else await other

    def if_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
        else_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return then_mapper(value) if predicate(value) else else_mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @as_awaitable_result
    async def aif_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
        else_mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return await then_mapper(value) if predicate(value) else await else_mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failure(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    def bind_many[TNewOut](
        self,
        mapper: Callable[[TOut], "EnumerableContextResult[TNewOut]"],
    ) -> "EnumerableContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failures(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    @as_awaitable_enumerable_result
    async def abind_many[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "EnumerableContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return await mapper(value)
            case ContextResult(tag="error", error=error):
                return ContextResult[TNewOut].failures(error)
            case _:
                raise TypeError(f"Unexpected result of type '{repr(self)}'")

    def to_unit(self) -> "ContextResult[Unit]":
        return self.map(lambda _: Unit())
