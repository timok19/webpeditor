import sys
from typing import final

from django.http.request import HttpRequest
from loguru import logger as loguru_logger

from webpeditor import settings
from webpeditor_app.core.abc.logger_abc import LoggerABC


@final
class Logger(LoggerABC):
    def __init__(self) -> None:
        loguru_logger.remove()
        loguru_logger.add(
            level="DEBUG" if settings.IS_DEVELOPMENT else "INFO",
            sink=sys.stderr,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> <level>{level: <8}</level> <cyan>{module}</cyan>:<yellow>{function}</yellow>:<white>{line}</white> - <level>{message}</level>",
        )

    @staticmethod
    def log_debug(message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(depth=depth).debug(message)

    @staticmethod
    def log_info(message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(depth=depth).info(message)

    @staticmethod
    def log_request_info(request: HttpRequest, message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(depth=depth).info(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def log_request_error(request: HttpRequest, message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(depth=depth).error(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def log_error(message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(depth=depth).error(message)

    @staticmethod
    def log_exception(exception: Exception, message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(exception=exception, colors=True, ansi=True, depth=depth).exception(message)

    @staticmethod
    def log_request_exception(request: HttpRequest, exception: Exception, message: str, *, depth: int = 1) -> None:
        return loguru_logger.opt(exception=exception, colors=True, ansi=True, depth=depth).exception(
            "Request {method} {path} - {message}, Exception:",
            method=request.method,
            path=request.path,
            message=message,
        )
