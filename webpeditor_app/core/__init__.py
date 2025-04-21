from anydi import Module, provider

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.webpeditor_logger import WebPEditorLogger


class CoreModule(Module):
    @provider(scope="singleton")
    def logger_provider(self) -> WebPEditorLoggerABC:
        return WebPEditorLogger()
