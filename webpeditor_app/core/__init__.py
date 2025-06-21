from anydi import Module, provider

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.webpeditor_logger import WebPEditorLogger

from webpeditor_app.core.error_context import ErrorContext
from webpeditor_app.core.decorators import acontext_result, aenumerable_context_result
from webpeditor_app.core.context_result import ContextResult
from webpeditor_app.core.awaitable_context_result import AwaitableContextResult
from webpeditor_app.core.enumerable_context_result import EnumerableContextResult
from webpeditor_app.core.awaitable_enumerable_context_result import AwaitableEnumerableContextResult

__all__: list[str] = [
    "ErrorContext",
    "ContextResult",
    "acontext_result",
    "aenumerable_context_result",
    "AwaitableContextResult",
    "EnumerableContextResult",
    "AwaitableEnumerableContextResult",
]


class CoreModule(Module):
    @provider(scope="singleton")
    def logger_provider(self) -> WebPEditorLoggerABC:
        return WebPEditorLogger()
