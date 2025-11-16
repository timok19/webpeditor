from anydi import Module, provider

from common.core.abc.logger_abc import LoggerABC
from common.core.logging.logger import Logger


class CoreModule(Module):
    @provider(scope="singleton")
    def provide_logger(self) -> LoggerABC:
        return Logger()
