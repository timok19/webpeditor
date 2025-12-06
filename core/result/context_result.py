import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, Collection, Generator, ParamSpec, TypeVar, override

from expression import Result
from types_linq import Enumerable

from core.result.error_context import ErrorContext

P = ParamSpec("P")
T = TypeVar("T")


def as_awaitable_result(func: Callable[P, Awaitable["ContextResult[T]"]]) -> Callable[P, "_AwaitableContextResult[T]"]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> "_AwaitableContextResult[T]":
        return _AwaitableContextResult[T](func(*args, **kwargs))

    return wrapper


def as_awaitable_enumerable_result(
    func: Callable[P, Awaitable["EnumerableContextResult[T]"]],
) -> Callable[P, "_AwaitableEnumerableContextResult[T]"]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> "_AwaitableEnumerableContextResult[T]":
        return _AwaitableEnumerableContextResult[T](func(*args, **kwargs))

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
        return ContextResult[TOut](tag="error", error=error)

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

    def as_empty(self) -> "ContextResult[None]":
        return self.map(lambda _: None)


class _AwaitableContextResult[TOut](Awaitable[ContextResult[TOut]]):
    def __init__(self, awaitable: Awaitable[ContextResult[TOut]]) -> None:
        self.__awaitable_result: Awaitable[ContextResult[TOut]] = awaitable

    def __await__(self) -> Generator[Any, Any, ContextResult[TOut]]:
        return self.__awaitable_result.__await__()

    @as_awaitable_result
    async def bind[TNewOut](self, mapper: Callable[[TOut], ContextResult[TNewOut]]) -> ContextResult[TNewOut]:
        return (await self).bind(mapper)

    @as_awaitable_result
    async def abind[TNewOut](self, mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]]) -> ContextResult[TNewOut]:
        return await (await self).abind(mapper)

    @as_awaitable_result
    async def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> ContextResult[TNewOut]:
        return (await self).map(mapper)

    @as_awaitable_result
    async def amap[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> ContextResult[TNewOut]:
        return await (await self).amap(mapper)

    @as_awaitable_result
    async def map2[TOutOther, TNewOut](
        self,
        other: ContextResult[TOutOther],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> ContextResult[TNewOut]:
        return (await self).map2(other, mapper)

    @as_awaitable_result
    async def amap1[TOutOther, TNewOut](
        self,
        other: Awaitable[TOutOther],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> ContextResult[TNewOut]:
        return await (await self).amap1(other, mapper)

    @as_awaitable_result
    async def amap2[TOutOther, TNewOut](
        self,
        other: Awaitable[ContextResult[TOutOther]],
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> ContextResult[TNewOut]:
        return await (await self).amap2(other, mapper)

    @as_awaitable_enumerable_result
    async def bind_many[TNewOut](self, mapper: Callable[[TOut], "EnumerableContextResult[TNewOut]"]) -> "EnumerableContextResult[TNewOut]":
        return (await self).bind_many(mapper)

    @as_awaitable_enumerable_result
    async def abind_many[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "EnumerableContextResult[TNewOut]":
        return await (await self).abind_many(mapper)

    @as_awaitable_result
    async def if_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], ContextResult[TNewOut]],
        else_mapper: Callable[[TOut], ContextResult[TNewOut]],
    ) -> ContextResult[TNewOut]:
        return (await self).if_then_else(predicate, then_mapper, else_mapper)

    @as_awaitable_result
    async def aif_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]],
        else_mapper: Callable[[TOut], Awaitable[ContextResult[TNewOut]]],
    ) -> ContextResult[TNewOut]:
        return await (await self).aif_then_else(predicate, then_mapper, else_mapper)

    @as_awaitable_result
    async def as_empty(self) -> ContextResult[None]:
        return (await self).as_empty()

    @as_awaitable_result
    async def filter_with(self, predicate: Callable[[TOut], bool], default: Callable[[TOut], ErrorContext]) -> ContextResult[TOut]:
        return ContextResult[TOut].from_result((await self).filter_with(predicate, default))


class EnumerableContextResult[TOut](Enumerable[ContextResult[TOut]]):
    @staticmethod
    def from_results(results: Collection[ContextResult[TOut]]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    @staticmethod
    @override
    def empty() -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut].from_results([])

    def if_then_else(
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], "EnumerableContextResult[TOut]"],
        else_mapper: Callable[[TOut], "EnumerableContextResult[TOut]"],
    ) -> "EnumerableContextResult[TOut]":
        cached = self.as_cached()
        errors = cached.where(lambda result: result.is_error()).select(lambda result: ContextResult[TOut].failure(result.error))
        mapped = (
            cached.where(lambda result: result.is_ok())
            .select(lambda result: result.ok)
            .select(lambda value: then_mapper(value) if predicate(value) else else_mapper(value))
            .select_many(lambda results: results)
        )

        return EnumerableContextResult[TOut].from_results(errors.concat(mapped))

    @as_awaitable_enumerable_result
    async def aif_then_else(
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], "Awaitable[EnumerableContextResult[TOut]]"],
        else_mapper: Callable[[TOut], "Awaitable[EnumerableContextResult[TOut]]"],
    ) -> "EnumerableContextResult[TOut]":
        cached = self.as_cached()
        errors = cached.where(lambda result: result.is_error()).select(lambda result: ContextResult[TOut].failure(result.error))
        mapped = Enumerable(
            await asyncio.gather(
                *cached.where(lambda result: result.is_ok())
                .select(lambda result: result.ok)
                .select(lambda value: then_mapper(value) if predicate(value) else else_mapper(value))
            )
        ).select_many(lambda results: results)

        return EnumerableContextResult[TOut].from_results(errors.concat(mapped))

    def if_empty(self, other: Enumerable[ContextResult[TOut]]) -> "EnumerableContextResult[TOut]":
        return self if self.any() else EnumerableContextResult[TOut].from_results(other)

    @as_awaitable_enumerable_result
    async def aif_empty(self, other: Awaitable[Enumerable[ContextResult[TOut]]]) -> "EnumerableContextResult[TOut]":
        return self if self.any() else EnumerableContextResult[TOut].from_results(await other)

    def tap_either(
        self,
        success_func: Callable[[Enumerable[TOut]], None] = lambda _: None,
        error_func: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> "EnumerableContextResult[TOut]":
        cached = self.as_cached()

        if cached.any(lambda result: result.is_error()):
            errors = cached.where(lambda result: result.is_error()).select(lambda result: result.error)
            error_func(errors)
            return EnumerableContextResult[TOut](errors.select(ContextResult[TOut].failure))

        values = cached.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        success_func(values)

        return EnumerableContextResult[TOut](values.select(ContextResult[TOut].success))


class _AwaitableEnumerableContextResult[TOut](Awaitable[EnumerableContextResult[TOut]]):
    def __init__(self, awaitable: Awaitable[EnumerableContextResult[TOut]]) -> None:
        self.__awaitable_results: Awaitable[EnumerableContextResult[TOut]] = awaitable

    def __await__(self) -> Generator[Any, Any, EnumerableContextResult[TOut]]:
        return self.__awaitable_results.__await__()

    @as_awaitable_enumerable_result
    async def if_then_else(
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], EnumerableContextResult[TOut]],
        else_mapper: Callable[[TOut], EnumerableContextResult[TOut]],
    ) -> EnumerableContextResult[TOut]:
        return (await self).if_then_else(predicate, then_mapper, else_mapper)

    @as_awaitable_enumerable_result
    async def aif_then_else(
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], Awaitable[EnumerableContextResult[TOut]]],
        else_mapper: Callable[[TOut], Awaitable[EnumerableContextResult[TOut]]],
    ) -> EnumerableContextResult[TOut]:
        return await (await self).aif_then_else(predicate, then_mapper, else_mapper)

    @as_awaitable_enumerable_result
    async def if_empty(self, other: Enumerable[ContextResult[TOut]]) -> EnumerableContextResult[TOut]:
        return (await self).if_empty(other)

    @as_awaitable_enumerable_result
    async def aif_empty(self, other: Awaitable[Enumerable[ContextResult[TOut]]]) -> EnumerableContextResult[TOut]:
        return await (await self).aif_empty(other)

    @as_awaitable_enumerable_result
    async def tap_either(
        self,
        success_func: Callable[[Enumerable[TOut]], None] = lambda _: None,
        error_func: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> EnumerableContextResult[TOut]:
        return (await self).tap_either(success_func, error_func)
