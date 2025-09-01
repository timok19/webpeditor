from typing import TYPE_CHECKING, Callable, Collection

from types_linq import Enumerable

from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.context_result import ContextResult


class EnumerableContextResult[TOut](Enumerable["ContextResult[TOut]"]):
    @staticmethod
    def from_results(results: Collection["ContextResult[TOut]"]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def tap_either(
        self,
        success_func: Callable[[Enumerable[TOut]], None] = lambda _: None,
        error_func: Callable[[Enumerable[ErrorContext]], None] = lambda _: None,
    ) -> "EnumerableContextResult[TOut]":
        from webpeditor_app.core.result.context_result import ContextResult

        if self.any(lambda result: result.is_error()):
            errors = self.where(lambda result: result.is_error()).select(lambda result: result.error)
            error_func(errors)
            return EnumerableContextResult[TOut](errors.select(ContextResult[TOut].failure))

        values = self.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        success_func(values)

        return EnumerableContextResult[TOut](values.select(ContextResult[TOut].success))
