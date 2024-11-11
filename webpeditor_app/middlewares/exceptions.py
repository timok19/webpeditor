from cloudinary.exceptions import Error as CloudinaryError
from typing import Callable

from django.http.request import HttpRequest
from django.http.response import HttpResponseBase, HttpResponseServerError

from webpeditor_app.core import get_dependency
from webpeditor_app.core.logging import LoggerABC


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response
        self.__logger: LoggerABC = get_dependency(LoggerABC)

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        try:
            return self.get_response(request)
        except CloudinaryError as ce:
            self.__logger.log_exception(ce, f"Cloudinary error: {ce}")
            # TODO: Change to a specific response such as ResultantResponse() etc...
            return HttpResponseServerError("Cloudinary error occurred")
        except Exception as e:
            self.__logger.log_request_exception_500(request, e)
            return HttpResponseServerError("An unexpected error occurred")
