from anydi import Module, provider

from core.abc.logger_abc import LoggerABC
from core.logging.logger import Logger


class CoreModule(Module):
    @provider(scope="singleton")
    def provide_logger(self) -> LoggerABC:
        return Logger()
