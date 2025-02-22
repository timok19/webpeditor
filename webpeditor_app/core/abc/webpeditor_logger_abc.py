from abc import ABC, abstractmethod

from django.http.request import HttpRequest


class WebPEditorLoggerABC(ABC):
    @staticmethod
    @abstractmethod
    def log_debug(message: str) -> None: ...

    @staticmethod
    @abstractmethod
    def log_info(message: str) -> None: ...

    @staticmethod
    @abstractmethod
    def log_request_info(request: HttpRequest, message: str) -> None: ...

    @staticmethod
    @abstractmethod
    def log_request_error(request: HttpRequest, message: str) -> None: ...

    @staticmethod
    @abstractmethod
    def log_error(message: str) -> None: ...

    @staticmethod
    @abstractmethod
    def log_exception(exception: Exception, message: str) -> None: ...

    @abstractmethod
    def log_exception_500(self, exception: Exception) -> None: ...

    @staticmethod
    @abstractmethod
    def log_request_exception(request: HttpRequest, exception: Exception, message: str) -> None: ...

    @abstractmethod
    def log_request_exception_500(self, request: HttpRequest, exception: Exception) -> None: ...
