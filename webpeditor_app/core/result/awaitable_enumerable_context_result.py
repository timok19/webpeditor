from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generator

from types_linq import Enumerable

from webpeditor_app.core.result.decorators import aenumerable_context_result
from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult


class AwaitableEnumerableContextResult[TOut](Awaitable["EnumerableContextResult[TOut]"]):
    def __init__(self, awaitable: Awaitable["EnumerableContextResult[TOut]"]) -> None:
        self.__awaitable_results: Awaitable["EnumerableContextResult[TOut]"] = awaitable

    def __await__(self) -> Generator[Any, Any, "EnumerableContextResult[TOut]"]:
        return self.__awaitable_results.__await__()

    @aenumerable_context_result
    async def log_results(
        self,
        log_success: Callable[[Enumerable[TOut]], None] = lambda _: None,
        log_error: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> "EnumerableContextResult[TOut]":
        return (await self.__awaitable_results).log_results(log_success, log_error)
