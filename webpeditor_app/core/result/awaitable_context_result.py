from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generator, Union

from webpeditor_app.core.result.decorators import acontext_result, aenumerable_context_result
from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.context_result import ContextResult
    from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult


class AwaitableContextResult[TOut](Awaitable["ContextResult[TOut]"]):
    def __init__(self, awaitable: Awaitable["ContextResult[TOut]"]) -> None:
        self.__awaitable_result: Awaitable["ContextResult[TOut]"] = awaitable

    def __await__(self) -> Generator[Any, Any, "ContextResult[TOut]"]:
        return self.__awaitable_result.__await__()

    @acontext_result
    async def bind[TNewOut](self, mapper: Callable[[TOut], "ContextResult[TNewOut]"]) -> "ContextResult[TNewOut]":
        async def _bind() -> "ContextResult[TNewOut]":
            return (await self.__awaitable_result).bind(mapper)

        return await _bind()

    @acontext_result
    async def abind[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["ContextResult[TNewOut]"]],
    ) -> "ContextResult[TNewOut]":
        async def _abind() -> "ContextResult[TNewOut]":
            return await (await self.__awaitable_result).abind(mapper)

        return await _abind()

    @acontext_result
    async def map[TNewOut](self, mapper: Callable[[TOut], TNewOut]) -> "ContextResult[TNewOut]":
        async def _map() -> "ContextResult[TNewOut]":
            return (await self.__awaitable_result).map(mapper)

        return await _map()

    @acontext_result
    async def amap[TNewOut](self, mapper: Callable[[TOut], Awaitable[TNewOut]]) -> "ContextResult[TNewOut]":
        async def _amap() -> "ContextResult[TNewOut]":
            return await (await self.__awaitable_result).amap(mapper)

        return await _amap()

    @acontext_result
    async def amap2[TOutOther, TNewOut](
        self,
        other: "ContextResult[TOutOther]",
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        async def _amap2() -> "ContextResult[TNewOut]":
            return await (await self.__awaitable_result).amap2(other, mapper)

        return await _amap2()

    @acontext_result
    async def amap3[TOutOther, TNewOut](
        self,
        other: "Awaitable[ContextResult[TOutOther]]",
        mapper: Callable[[TOut, TOutOther], TNewOut],
    ) -> "ContextResult[TNewOut]":
        async def _amap2() -> "ContextResult[TNewOut]":
            return await (await self.__awaitable_result).amap2(await other, mapper)

        return await _amap2()

    @aenumerable_context_result
    async def abind_many[TNewOut](
        self,
        mapper: Callable[[TOut], "EnumerableContextResult[TNewOut]"],
    ) -> "EnumerableContextResult[TNewOut]":
        async def _abind_many() -> "EnumerableContextResult[TNewOut]":
            return (await self.__awaitable_result).bind_many(mapper)

        return await _abind_many()

    @aenumerable_context_result
    async def abind_many2[TNewOut](
        self,
        mapper: Callable[[TOut], Awaitable["EnumerableContextResult[TNewOut]"]],
    ) -> "EnumerableContextResult[TNewOut]":
        async def _abind_many() -> "EnumerableContextResult[TNewOut]":
            return await (await self.__awaitable_result).abind_many(mapper)

        return await _abind_many()

    @acontext_result
    async def alog_match(
        self,
        success_func: Callable[[TOut], str],
        error_func: Callable[[ErrorContext], str],
    ) -> "ContextResult[TOut]":
        async def _alog_match() -> "ContextResult[TOut]":
            return (await self.__awaitable_result).log_match(success_func, error_func)

        return await _alog_match()

    @acontext_result
    async def or_else(self, other: "ContextResult[TOut]") -> "ContextResult[TOut]":
        async def _or_else() -> "ContextResult[TOut]":
            return (await self.__awaitable_result).or_else(other)

        return await _or_else()

    @acontext_result
    async def aor_else(self, other: Awaitable["ContextResult[TOut]"]) -> "ContextResult[TOut]":
        async def _aor_else() -> "ContextResult[TOut]":
            result = await self.__awaitable_result
            return result if result.is_ok() else await other

        return await _aor_else()

    @acontext_result
    async def if_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], bool],
        then_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
        else_mapper: Callable[[TOut], "ContextResult[TNewOut]"],
    ) -> "ContextResult[TNewOut]":
        async def _if_then_else() -> "ContextResult[TNewOut]":
            return (await self.__awaitable_result).if_then_else(predicate, then_mapper, else_mapper)

        return await _if_then_else()

    @acontext_result
    async def aif_then_else[TNewOut](
        self,
        predicate: Callable[[TOut], Union[bool, Awaitable[bool]]],
        then_mapper: Callable[[TOut], Union["ContextResult[TNewOut]", Awaitable["ContextResult[TNewOut]"]]],
        else_mapper: Callable[[TOut], Union["ContextResult[TNewOut]", Awaitable["ContextResult[TNewOut]"]]],
    ) -> "ContextResult[TNewOut]":
        async def _aif_then_else() -> "ContextResult[TNewOut]":
            return await (await self.__awaitable_result).aif_then_else(predicate, then_mapper, else_mapper)

        return await _aif_then_else()
