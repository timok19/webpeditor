from webpeditor_app.core.result.decorators import acontext_result, aenumerable_context_result
from webpeditor_app.core.result.error_context import ErrorContext
from webpeditor_app.core.result.context_result import ContextResult
from webpeditor_app.core.result.awaitable_context_result import AwaitableContextResult
from webpeditor_app.core.result.enumerable_context_result import EnumerableContextResult
from webpeditor_app.core.result.awaitable_enumerable_context_result import AwaitableEnumerableContextResult

__all__: list[str] = [
    "ErrorContext",
    "ContextResult",
    "acontext_result",
    "aenumerable_context_result",
    "AwaitableContextResult",
    "EnumerableContextResult",
    "AwaitableEnumerableContextResult",
]
