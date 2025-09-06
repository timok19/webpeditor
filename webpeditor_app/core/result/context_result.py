from functools import wraps
from typing import Awaitable, Callable, override, Any, Generator, ParamSpec, TypeVar, Collection

from expression import Result
from types_linq import Enumerable

from webpeditor_app.core.result.error_context import ErrorContext
from webpeditor_app.types import Unit


P = ParamSpec("P")
T = TypeVar("T")


def as_awaitable_result(func: Callable[P, Awaitable["ContextResult[T]"]]) -> Callable[P, "AwaitableContextResult[T]"]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> "AwaitableContextResult[T]":
        return AwaitableContextResult[T](func(*args, **kwargs))

    return wrapper


def as_awaitable_enumerable_result(
    func: Callable[P, Awaitable["EnumerableContextResult[T]"]],
) -> Callable[P, "AwaitableEnumerableContextResult[T]"]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> "AwaitableEnumerableContextResult[T]":
        return AwaitableEnumerableContextResult[T](func(*args, **kwargs))

    return wrapper


class ContextResult[TOut](Result[TOut, ErrorContext]):
    @staticmethod
    def success(value: TOut) -> "ContextResult[TOut]":
        return ContextResult[TOut](tag="ok", ok=value)

    @classmethod
    @as_awaitable_result
    async def asuccess(cls, value: TOut) -> "ContextResult[TOut]":
        return cls.success(value)

    @staticmethod
    def failure(error: ErrorContext) -> "ContextResult[TOut]":
        return ContextResult[TOut](
            tag="error",
            error=ErrorContext(
                error_code=error.error_code,
                message=error.message or "",
                reasons=error.reasons or [],
            ),
        )

    @classmethod
    def failures(cls, *errors: ErrorContext) -> "EnumerableContextResult[TOut]":
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
    async def amap1[TOutOther, TNewOut](
        self,
        other: Awaitable[TOutOther],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        match self:
            case ContextResult(tag="ok", ok=value):
                return ContextResult[TNewOut].success(mapper(value, await other))
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
        return self.or_else(await other)

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


class AwaitableContextResult[TOut](Awaitable[ContextResult[TOut]]):
    def __init__(self, awaitable: Awaitable[ContextResult[TOut]]) -> None:
        self.__awaitable_result: Awaitable[ContextResult[TOut]] = awaitable

    def __await__(self) -> Generator[Any, Any, ContextResult[TOut]]:
        return self.__awaitable_result.__await__()

    @as_awaitable_result
    async def bind[TNewOut](self, mapper: Callable[[TOut], ContextResult[TNewOut]]) -> ContextResult[TNewOut]:
        return (await self.__awaitable_result).bind(mapper)

    @as_awaitable_result
    async def abind[TNewOut](self, mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]]) -> ContextResult[TNewOut]:
        return await (await self.__awaitable_result).abind(mapper)

    @as_awaitable_result
    async def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> ContextResult[TNewOut]:
        return (await self.__awaitable_result).map(mapper)

    @as_awaitable_result
    async def amap[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> ContextResult[TNewOut]:
        return await (await self.__awaitable_result).amap(mapper)

    @as_awaitable_result
    async def map2[TOutOther, TNewOut](
        self,
        other: ContextResult[TOutOther],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> ContextResult[TNewOut]:
        return (await self.__awaitable_result).map2(other, mapper)

    @as_awaitable_result
    async def amap1[TOutOther, TNewOut](
        self,
        other: Awaitable[TOutOther],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> ContextResult[TNewOut]:
        return await (await self.__awaitable_result).amap1(other, mapper)

    @as_awaitable_result
    async def amap2[TOutOther, TNewOut](
        self,
        other: Awaitable[ContextResult[TOutOther]],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> ContextResult[TNewOut]:
        return await (await self.__awaitable_result).amap2(other, mapper)

    @as_awaitable_enumerable_result
    async def bind_many[TNewOut](self, mapper: Callable[[TOut], "EnumerableContextResult[TNewOut]"]) -> "EnumerableContextResult[TNewOut]":
        return (await self.__awaitable_result).bind_many(mapper)

    @as_awaitable_enumerable_result
    async def abind_many[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "EnumerableContextResult[TNewOut]":
        return await (await self.__awaitable_result).abind_many(mapper)

    @as_awaitable_result
    async def if_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], ContextResult[TNewOut]],
        else_mapper: Callable[[TOut], ContextResult[TNewOut]],
    ) -> ContextResult[TNewOut]:
        return (await self.__awaitable_result).if_then_else(predicate, then_mapper, else_mapper)

    @as_awaitable_result
    async def aif_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]],
        else_mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]],
    ) -> ContextResult[TNewOut]:
        return await (await self.__awaitable_result).aif_then_else(predicate, then_mapper, else_mapper)

    @as_awaitable_result
    async def to_unit(self) -> ContextResult[Unit]:
        return (await self.__awaitable_result).to_unit()

    @as_awaitable_result
    async def filter_with(self, predicate: Callable[[TOut], bool], default: Callable[[TOut], ErrorContext]) -> ContextResult[TOut]:
        return ContextResult[TOut].from_result((await self.__awaitable_result).filter_with(predicate, default))


class EnumerableContextResult[TOut](Enumerable[ContextResult[TOut]]):
    @staticmethod
    def from_results(results: Collection[ContextResult[TOut]]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def tap_either(
        self,
        success_func: Callable[[Enumerable[TOut]], None] = lambda _: None,
        error_func: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> "EnumerableContextResult[TOut]":
        if self.any(lambda result: result.is_error()):
            errors = self.where(lambda result: result.is_error()).select(lambda result: result.error)
            error_func(errors)
            return EnumerableContextResult[TOut](errors.select(ContextResult[TOut].failure))

        values = self.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        success_func(values)

        return EnumerableContextResult[TOut](values.select(ContextResult[TOut].success))


class AwaitableEnumerableContextResult[TOut](Awaitable[EnumerableContextResult[TOut]]):
    def __init__(self, awaitable: Awaitable[EnumerableContextResult[TOut]]) -> None:
        self.__awaitable_results: Awaitable[EnumerableContextResult[TOut]] = awaitable

    def __await__(self) -> Generator[Any, Any, EnumerableContextResult[TOut]]:
        return self.__awaitable_results.__await__()

    @as_awaitable_enumerable_result
    async def tap_either(
        self,
        success_func: Callable[[Enumerable[TOut]], None] = lambda _: None,
        error_func: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> EnumerableContextResult[TOut]:
        return (await self.__awaitable_results).tap_either(success_func, error_func)
