import json
from typing import Callable, Final


from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from ninja.responses import codes_4xx, codes_5xx
from types_linq import Enumerable

from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response
        from webpeditor_app.common.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        return self.__process_response(request, self.get_response(request))

    def __process_response(self, request: HttpRequest, response: HttpResponseBase) -> HttpResponseBase:
        error_codes = Enumerable(codes_4xx).union(codes_5xx)

        if isinstance(response, HttpResponse) and error_codes.any(lambda code: response.status_code == code):
            response_data: object = json.loads(response.content)

            if isinstance(response_data, list):
                for item in response_data:
                    if isinstance(item, dict) and "message" in item:
                        self.__logger.log_request_error(request, item["message"])

            if isinstance(response_data, dict) and "message" in response_data:
                self.__logger.log_request_error(request, response_data["message"])

        return response
