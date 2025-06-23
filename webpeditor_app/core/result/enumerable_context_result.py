from typing import TYPE_CHECKING, Callable, Collection, Final

from types_linq import Enumerable

from webpeditor_app.core import WebPEditorLoggerABC
from webpeditor_app.core.result.error_context import ErrorContext

if TYPE_CHECKING:
    from webpeditor_app.core.result.context_result import ContextResult


class EnumerableContextResult[TOut](Enumerable["ContextResult[TOut]"]):
    @staticmethod
    def from_results(results: Collection["ContextResult[TOut]"]) -> "EnumerableContextResult[TOut]":
        return EnumerableContextResult[TOut](results)

    def log_match(
        self,
        success_func: Callable[[Enumerable[TOut]], str],
        error_func: Callable[[Enumerable[ErrorContext]], str],
    ) -> "EnumerableContextResult[TOut]":
        from webpeditor_app.core.result.context_result import ContextResult
        from anydi.ext.django import container

        logger: Final[WebPEditorLoggerABC] = container.resolve(WebPEditorLoggerABC)

        if self.any(lambda result: result.is_error()):
            errors = self.where(lambda result: result.is_error()).select(lambda result: result.error)
            logger.log_error(error_func(errors))

            return EnumerableContextResult(errors.select(ContextResult[TOut].failure))

        values = self.where(lambda result: result.is_ok()).select(lambda result: result.ok)
        logger.log_info(success_func(values))
        return EnumerableContextResult(values.select(ContextResult[TOut].success))
