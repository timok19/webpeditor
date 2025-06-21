from typing import Awaitable, Any, Generator, Callable, TYPE_CHECKING

from types_linq import Enumerable

from webpeditor_app.core.result.decorators import aenumerable_context_result
from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult


class AwaitableEnumerableContextResult[TOut](Awaitable["EnumerableContextResult[TOut]"]):
    def __init__(self, awaitable: Awaitable["EnumerableContextResult[TOut]"]) -> None:
        self.__awaitable_result: Awaitable["EnumerableContextResult[TOut]"] = awaitable

    def __await__(self) -> Generator[Any, Any, "EnumerableContextResult[TOut]"]:
        return self.__awaitable_result.__await__()

    @aenumerable_context_result
    async def match(
        self,
        success_func: Callable[[Enumerable[TOut]], Enumerable[TOut]],
        error_func: Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]],
    ) -> "EnumerableContextResult[TOut]":
        async def _amatch() -> "EnumerableContextResult[TOut]":
            return (await self.__awaitable_result).match(success_func, error_func)

        return await _amatch()
