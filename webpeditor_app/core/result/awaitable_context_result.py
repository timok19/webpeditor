from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generator

from webpeditor_app.core.result.decorators import acontext_result, aenumerable_context_result

if TYPE_CHECKING:
    from webpeditor_app.core.result.context_result import ContextResult
    from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult
    from webpeditor_app.core.result.error_context import ErrorContext


class AwaitableContextResult[TOut](Awaitable["ContextResult[TOut]"]):
    def __init__(self, awaitable: Awaitable["ContextResult[TOut]"]) -> None:
        self.__awaitable_result: Awaitable["ContextResult[TOut]"] = awaitable

    def __await__(self) -> Generator[Any, Any, "ContextResult[TOut]"]:
        return self.__awaitable_result.__await__()

    @acontext_result
    async def bind[TNewOut](self, mapper: Callable[[TOut], "ContextResult[TNewOut]"]) -> "ContextResult[TNewOut]":
        return (await self.__awaitable_result).bind(mapper)

    @acontext_result
    async def abind[TNewOut](self, mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]]) -> "ContextResult[TNewOut]":
        return await (await self.__awaitable_result).abind(mapper)

    @acontext_result
    async def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        return (await self.__awaitable_result).map(mapper)

    @acontext_result
    async def amap[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "ContextResult[TNewOut]":
        return await (await self.__awaitable_result).amap(mapper)

    @acontext_result
    async def map2[TOutOther, TNewOut](
        self,
        other: "ContextResult[TOutOther]",
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        return (await self.__awaitable_result).map2(other, mapper)

    @acontext_result
    async def amap2[TOutOther, TNewOut](
        self,
        other: "Awaitable[ContextResult[TOutOther]]",
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        return await (await self.__awaitable_result).amap2(other, mapper)

    @aenumerable_context_result
    async def bind_many[TNewOut](self, mapper: Callable[[TOut], "EnumerableContextResult[TNewOut]"]) -> "EnumerableContextResult[TNewOut]":
        return (await self.__awaitable_result).bind_many(mapper)

    @aenumerable_context_result
    async def abind_many[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "EnumerableContextResult[TNewOut]":
        return await (await self.__awaitable_result).abind_many(mapper)

    @acontext_result
    async def log_result(
        self,
        log_success: Callable[[TOut], None] = lambda _: None,
        log_error: Callable[["ErrorContext"], None] = lambda _: None,
    ) -> "ContextResult[TOut]":
        return (await self.__awaitable_result).log_result(log_success, log_error)

    @acontext_result
    async def or_else(self, other: "ContextResult[TOut]") -> "ContextResult[TOut]":
        return (await self.__awaitable_result).or_else(other)

    @acontext_result
    async def aor_else(self, other: Awaitable["ContextResult[TOut]"]) -> "ContextResult[TOut]":
        return await (await self.__awaitable_result).aor_else(other)

    @acontext_result
    async def if_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
        else_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
    ) -> "ContextResult[TNewOut]":
        return (await self.__awaitable_result).if_then_else(predicate, then_mapper, else_mapper)

    @acontext_result
    async def aif_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
        else_mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
    ) -> "ContextResult[TNewOut]":
        return await (await self.__awaitable_result).aif_then_else(predicate, then_mapper, else_mapper)
