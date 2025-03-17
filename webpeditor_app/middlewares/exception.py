import json
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from expression import Success, Failure, Try
from ninja.responses import codes_4xx, codes_5xx
from types_linq import Enumerable
from typing import Callable, Final, cast, final

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC


@final
class ExceptionHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        return self.__process(request, self.get_response(request))

    def __process(self, request: HttpRequest, response: HttpResponseBase) -> HttpResponseBase:
        return (
            self.__process_http_error_response(request, response)
            if isinstance(response, HttpResponse) and self.__is_error_response(response.status_code)
            else response
        )

    @staticmethod
    def __is_error_response(status_code: int) -> bool:
        return Enumerable(codes_4xx).union(codes_5xx).any(lambda code: status_code == code)

    def __process_http_error_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # TODO: user pydantic json validation instead of manual
        response_data_result = self.__get_response_data(response.content)

        if response_data_result.is_error():
            self.__logger.log_request_exception(
                request,
                response_data_result.error,
                f"Unhandled error. Reason: '{response.content.decode()}'",
            )
            return response

        response_data = response_data_result.ok

        if isinstance(response_data, list):
            for item in response_data:
                if isinstance(item, dict):
                    data = cast(dict[str, object], item)
                    self.__log_mapped_error(request, data)
        elif isinstance(response_data, dict):
            data = cast(dict[str, object], response_data)
            self.__log_mapped_error(request, data)
        else:
            self.__logger.log_request_error(request, f"Unhandled error. Reason: {response.content.decode()}")

        return response

    @staticmethod
    def __get_response_data(content: bytes) -> Try[object]:
        try:
            return Success(json.loads(content))
        except Exception as exc:
            return Failure(exc)

    def __log_mapped_error(self, request: HttpRequest, data: dict[str, object]) -> None:
        if "message" in data and "reasons" in data:
            reasons = cast(list[str], data["reasons"])
            self.__logger.log_request_error(
                request, f"{data['message']}. Reasons: [{', '.join(reasons) if len(reasons) > 0 else ''}]"
            )
        else:
            self.__logger.log_request_error(request, "Unexpected response")
