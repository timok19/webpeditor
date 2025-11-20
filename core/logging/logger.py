import sys
from typing import final

import loguru
from django.http.request import HttpRequest

from webpeditor import settings
from core.abc.logger_abc import LoggerABC


@final
class Logger(LoggerABC):
    def __init__(self) -> None:
        loguru.logger.remove()
        loguru.logger.add(
            sys.stderr,
            level="DEBUG" if settings.IS_DEVELOPMENT else "INFO",
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> <level>{level: <8}</level> <cyan>{module}</cyan>:<yellow>{function}</yellow>:<white>{line}</white> - <level>{message}</level>",
        )

    def debug(self, message: str) -> None:
        return loguru.logger.opt(depth=1).debug(message)

    def info(self, message: str) -> None:
        return loguru.logger.opt(depth=1).info(message)

    def request_info(self, request: HttpRequest, message: str) -> None:
        return loguru.logger.opt(depth=1).info(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    def request_error(self, request: HttpRequest, message: str) -> None:
        return loguru.logger.opt(depth=1).error(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    def error(self, message: str) -> None:
        return loguru.logger.opt(depth=1).error(message)

    def exception(self, exception: Exception, message: str) -> None:
        return loguru.logger.opt(exception=exception, depth=1).exception(message)

    def request_exception(self, request: HttpRequest, exception: Exception, message: str) -> None:
        return loguru.logger.opt(exception=exception, depth=1).exception(
            "Request {method} {path} - {message}, Exception:",
            method=request.method,
            path=request.path,
            message=message,
        )
