from abc import ABC, abstractmethod

from django.http.request import HttpRequest


class WebPEditorLoggerABC(ABC):
    @staticmethod
    @abstractmethod
    def log_debug(message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def log_info(message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def log_request_info(request: HttpRequest, message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def log_request_error(request: HttpRequest, message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def log_error(message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def log_exception(exception: Exception, message: str, *, depth: int = 1) -> None: ...

    @staticmethod
    @abstractmethod
    def log_request_exception(request: HttpRequest, exception: Exception, message: str, *, depth: int = 1) -> None: ...
