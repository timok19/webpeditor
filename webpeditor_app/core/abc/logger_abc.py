from abc import ABC, abstractmethod

from django.http.request import HttpRequest


class LoggerABC(ABC):
    @staticmethod
    @abstractmethod
    def debug(message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def info(message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def request_info(request: HttpRequest, message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def request_error(request: HttpRequest, message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def error(message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def exception(exception: Exception, message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def request_exception(request: HttpRequest, exception: Exception, message: str, *, depth: int = 1) -> None: ...
