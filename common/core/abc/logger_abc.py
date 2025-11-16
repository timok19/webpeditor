from abc import ABC, abstractmethod

from django.http.request import HttpRequest


class LoggerABC(ABC):
    @abstractmethod
    def debug(self, message: str) -> None: ...

    @abstractmethod
    def info(self, message: str) -> None: ...

    @abstractmethod
    def request_info(self, request: HttpRequest, message: str) -> None: ...

    @abstractmethod
    def request_error(self, request: HttpRequest, message: str) -> None: ...

    @abstractmethod
    def error(self, message: str) -> None: ...

    @abstractmethod
    def exception(self, exception: Exception, message: str) -> None: ...

    @abstractmethod
    def request_exception(self, request: HttpRequest, exception: Exception, message: str) -> None: ...
