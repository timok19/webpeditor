from anydi.ext.django import container
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from ninja.responses import codes_4xx, codes_5xx
from pydantic import ValidationError
from types_linq import Enumerable
from typing import Any, Callable, final, Final

from webpeditor_app.controllers.schemas import HTTPResult
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result.context_result import ContextResult
from webpeditor_app.core.result.error_context import ErrorContext


@final
class ErrorHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = container.resolve(WebPEditorLoggerABC)
        self.get_response: Callable[[HttpRequest], HttpResponseBase] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        return (
            self.__process_error_response(request, response)
            if isinstance(response, HttpResponse) and self.__is_error_response(response.status_code)
            else response
        )

    @staticmethod
    def __is_error_response(status_code: int) -> bool:
        return Enumerable(codes_4xx).union(codes_5xx).any(lambda code: status_code == code)

    def __process_error_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        validation_result = self.__validate_json(request, response)

        # Skip error logging if a response object is not "HTTPResult"
        if validation_result.is_error():
            return response

        http_errors = Enumerable(validation_result.ok.errors)
        message = f"Errors: [{'; '.join(http_errors.select(lambda error: f'(Message: "{error.message}" | Reasons: [{", ".join(error.reasons)}])'))}]"

        self.__logger.log_request_error(request, message)

        return response

    def __validate_json(self, request: HttpRequest, response: HttpResponse) -> ContextResult[HTTPResult[Any]]:
        try:
            return ContextResult[HTTPResult[Any]].success(HTTPResult[Any].model_validate_json(response.content))
        except ValidationError:
            return ContextResult[HTTPResult[Any]].failure(ErrorContext.server_error())
        except Exception as exception:
            self.__logger.log_request_exception(request, exception, f"Unhandled error. Reason: '{response.text}'")
            return ContextResult[HTTPResult[Any]].failure(ErrorContext.server_error())
