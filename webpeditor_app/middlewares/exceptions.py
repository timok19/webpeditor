import json
from typing import Callable, Final


from django.http.request import HttpRequest
from django.http.response import HttpResponse
from ninja.responses import codes_4xx, codes_5xx

from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        from webpeditor_app.common.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.__process_response(request, self.get_response(request))

    def __process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        if response.status_code in codes_4xx or response.status_code in codes_5xx:
            response_data: object = json.loads(response.content)

            if isinstance(response_data, list):
                for item in response_data:
                    if isinstance(item, dict) and "message" in item:
                        self.__logger.log_request_error(request, item["message"])

            if isinstance(response_data, dict):
                if "message" in response_data:
                    self.__logger.log_request_error(request, response_data["message"])

        return response
