import sys
from typing import final

import loguru
from django.http.request import HttpRequest

from webpeditor import settings
from webpeditor_app.core.abc.logger_abc import LoggerABC


@final
class Logger(LoggerABC):
    def __init__(self) -> None:
        loguru.logger.remove()
        loguru.logger.add(
            level="DEBUG" if settings.IS_DEVELOPMENT else "INFO",
            sink=sys.stderr,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> <level>{level: <8}</level> <cyan>{module}</cyan>:<yellow>{function}</yellow>:<white>{line}</white> - <level>{message}</level>",
        )

    @staticmethod
    def debug(message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(depth=depth).debug(message)

    @staticmethod
    def info(message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(depth=depth).info(message)

    @staticmethod
    def request_info(request: HttpRequest, message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(depth=depth).info(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def request_error(request: HttpRequest, message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(depth=depth).error(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def error(message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(depth=depth).error(message)

    @staticmethod
    def exception(exception: Exception, message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(exception=exception, depth=depth).exception(message)

    @staticmethod
    def request_exception(request: HttpRequest, exception: Exception, message: str, *, depth: int = 1) -> None:
        return loguru.logger.opt(exception=exception, depth=depth).exception(
            "Request {method} {path} - {message}, Exception:",
            method=request.method,
            path=request.path,
            message=message,
        )
