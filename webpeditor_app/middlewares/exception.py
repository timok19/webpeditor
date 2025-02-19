import json
from typing import Callable, Final

from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from ninja.responses import codes_4xx, codes_5xx
from returns.pipeline import is_successful
from returns.result import attempt, Result
from types_linq import Enumerable

from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response
        from webpeditor_app.core.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        return self.__process_response(request, self.get_response(request))

    def __process_response(self, request: HttpRequest, response: HttpResponseBase) -> HttpResponseBase:
        error_codes = Enumerable(codes_4xx).union(codes_5xx)

        if isinstance(response, HttpResponse) and error_codes.any(lambda code: response.status_code == code):
            return self.__process_http_error_response(request, response)

        return response

    def __process_http_error_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        response_data_result: Result[object, bytes] = self.__get_response_data(response.content)

        if not is_successful(response_data_result):
            content = response_data_result.failure().decode()
            self.__logger.log_request_error(request, f"Error parsing response content. Content: '{content}'")
            return response

        response_data = response_data_result.unwrap()

        if isinstance(response_data, list):
            for item in response_data:
                if isinstance(item, dict):
                    self.__log_mapped_error(request, item)
        elif isinstance(response_data, dict):
            self.__log_mapped_error(request, response_data)
        else:
            self.__logger.log_request_error(request, f"Unhandled error. Reason: {response.content.decode()}")

        return response

    @staticmethod
    @attempt
    def __get_response_data(content: bytes) -> object:
        return json.loads(content)

    def __log_mapped_error(self, request: HttpRequest, data: dict[str, object]) -> None:
        self.__logger.log_request_error(request, data["message"] if "message" in data else "Unexpected response")
