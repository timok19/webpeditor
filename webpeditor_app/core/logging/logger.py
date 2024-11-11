import sys

from django.http.request import HttpRequest
from loguru import logger

from webpeditor_app.core.logging.logger_abc import LoggerABC


class Logger(LoggerABC):
    def __init__(self) -> None:
        logger.remove()
        logger.add(
            sink=sys.stderr,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        )

    @staticmethod
    def log_info(message: str) -> None:
        logger.info(message)

    @staticmethod
    def log_request_info(request: HttpRequest, message: str) -> None:
        logger.info(
            "Request {method} {path} - {message}",
            method=request.method,
            path=request.path,
            message=message,
        )

    @staticmethod
    def log_error(message: str) -> None:
        logger.error(message)

    @staticmethod
    def log_exception(exception: Exception, message: str) -> None:
        logger.opt(exception=exception, colors=True, ansi=True).exception(message)

    def log_exception_500(self, exception: Exception) -> None:
        self.log_exception(exception, "Internal server error")

    @staticmethod
    def log_request_exception(request: HttpRequest, exception: Exception, message: str) -> None:
        logger.opt(exception=exception, colors=True, ansi=True).exception(
            "Request {method} {path} - {message}, Exception:",
            method=request.method,
            path=request.path,
            message=message,
        )

    def log_request_exception_500(self, request: HttpRequest, exception: Exception) -> None:
        self.log_request_exception(request, exception, "Internal server error")
