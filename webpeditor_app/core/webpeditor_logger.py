import sys
from typing import final

from django.http.request import HttpRequest
from loguru import logger

from webpeditor.settings import DEBUG
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC


@final
class WebPEditorLogger(WebPEditorLoggerABC):
    def __init__(self) -> None:
        logger.remove()
        logger.add(
            level="DEBUG" if DEBUG else "INFO",
            sink=sys.stderr,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <6}</level> | {module}:{function}:{line} - <level>{message}</level>",
        )

    @staticmethod
    def log_debug(message: str) -> None:
        logger.opt(depth=1).debug(message)

    @staticmethod
    def log_info(message: str) -> None:
        logger.opt(depth=1).info(message)

    @staticmethod
    def log_request_info(request: HttpRequest, message: str) -> None:
        logger.opt(depth=1).info(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def log_request_error(request: HttpRequest, message: str) -> None:
        logger.opt(depth=1).error(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def log_error(message: str) -> None:
        logger.opt(depth=1).error(message)

    @staticmethod
    def log_exception(exception: Exception, message: str) -> None:
        logger.opt(exception=exception, colors=True, ansi=True, depth=1).exception(message)

    def log_exception_500(self, exception: Exception) -> None:
        self.log_exception(exception, "Internal server error")

    @staticmethod
    def log_request_exception(request: HttpRequest, exception: Exception, message: str) -> None:
        logger.opt(exception=exception, colors=True, ansi=True, depth=1).exception(
            "Request {method} {path} - {message}, Exception:",
            method=request.method,
            path=request.path,
            message=message,
        )

    def log_request_exception_500(self, request: HttpRequest, exception: Exception) -> None:
        self.log_request_exception(request, exception, "Internal server error")
