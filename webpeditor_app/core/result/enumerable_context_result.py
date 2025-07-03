from typing import TYPE_CHECKING, Callable, Collection

from types_linq import Enumerable

from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.context_result import ContextResult


class EnumerableContextResult[TOut](Enumerable["ContextResult[TOut]"]):
    @staticmethod
    def from_results(results: Collection["ContextResult[TOut]"]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def log_results(
        self,
        log_success: Callable[[Enumerable[TOut]], None],
        log_error: Callable[[Enumerable[ErrorContext]], None],
    ) -> "EnumerableContextResult[TOut]":
        from webpeditor_app.core.result.context_result import ContextResult

        if self.any(lambda result: result.is_error()):
            errors = self.where(lambda result: result.is_error()).select(lambda result: result.error)
            log_error(errors)
            return EnumerableContextResult(errors.select(ContextResult[TOut].failure))

        values = self.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        log_success(values)
        return EnumerableContextResult(values.select(ContextResult[TOut].success))
