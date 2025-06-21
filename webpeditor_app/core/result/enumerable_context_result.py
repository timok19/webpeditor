from typing import Callable, Collection, TYPE_CHECKING

from types_linq import Enumerable

from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.context_result import ContextResult


class EnumerableContextResult[TOut](Enumerable["ContextResult[TOut]"]):
    @staticmethod
    def from_results(results: Collection["ContextResult[TOut]"]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def match(
        self,
        success_func: Callable[[Enumerable[TOut]], Enumerable[TOut]],
        error_func: Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]],
    ) -> "EnumerableContextResult[TOut]":
        from webpeditor_app.core.result.context_result import ContextResult

        if self.any(lambda result: result.is_error()):
            errors = self.where(lambda result: result.is_error()).select(lambda result: result.error)
            return EnumerableContextResult(error_func(errors).select(ContextResult[TOut].failure))

        values = self.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        return EnumerableContextResult(success_func(values).select(ContextResult[TOut].success))
