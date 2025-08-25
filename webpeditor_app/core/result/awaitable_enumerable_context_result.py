from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generator

from types_linq import Enumerable

from webpeditor_app.core.result.decorators import as_awaitable_enumerable_result
from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult


class AwaitableEnumerableContextResult[TOut](Awaitable["EnumerableContextResult[TOut]"]):
    def __init__(self, awaitable: Awaitable["EnumerableContextResult[TOut]"]) -> None:
        self.__awaitable_results: Awaitable["EnumerableContextResult[TOut]"] = awaitable

    def __await__(self) -> Generator[Any, Any, "EnumerableContextResult[TOut]"]:
        return self.__awaitable_results.__await__()

    @as_awaitable_enumerable_result
    async def tap_either(
        self,
        success_func: Callable[[Enumerable[TOut]], None] = lambda _: None,
        error_func: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> "EnumerableContextResult[TOut]":
        return (await self.__awaitable_results).tap_either(success_func, error_func)
