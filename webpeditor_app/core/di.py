from anydi import Module, provider

from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.logging.logger import Logger


class CoreModule(Module):
    @provider(scope="singleton")
    def provide_logger(self) -> LoggerABC:
        return Logger()
