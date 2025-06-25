from typing import Any, Callable, Collection, Final, final, cast

from anydi.ext.django import container
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from expression import Option
from ninja.responses import codes_4xx, codes_5xx
from pydantic import ValidationError
from types_linq import Enumerable

from webpeditor_app.controllers.schemas import HTTPResult
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC


@final
class ErrorHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = container.resolve(WebPEditorLoggerABC)
        self.get_response: Callable[[HttpRequest], HttpResponseBase] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        return self.__process(request, cast(HttpResponse, response)) if self.__is_error_response(response) else response

    @staticmethod
    def __is_error_response(response: HttpResponseBase) -> bool:
        return isinstance(response, HttpResponse) and Enumerable(codes_4xx).union(codes_5xx).any(lambda code: response.status_code == code)

    def __process(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        validation_result = self.__validate_json(request, response)

        # Skip error logging if a response object is not "HTTPResult"
        if validation_result.is_none():
            return response

        message = self.__get_error_message(validation_result.some.errors)

        self.__logger.log_request_error(request, message)

        return response

    def __validate_json(self, request: HttpRequest, response: HttpResponse) -> Option[HTTPResult[Any]]:
        try:
            return Option[HTTPResult[Any]].Some(HTTPResult[Any].model_validate_json(response.content))
        except ValidationError as validation_error:
            self.__logger.log_debug(validation_error.json(indent=4))
            return Option[HTTPResult[Any]].Nothing()
        except Exception as exception:
            self.__logger.log_request_exception(request, exception, f"Unhandled error. Reason: '{response.text}'")
            return Option[HTTPResult[Any]].Nothing()

    def __get_error_message(self, errors: Collection[HTTPResult.HTTPError]) -> str:
        return f"Errors: [{'; '.join(f'(Message: "{e.message}" | Reasons: [{self.__reasons_to_str(e.reasons)}])' for e in errors)}]"

    @staticmethod
    def __reasons_to_str(reasons: Collection[str]) -> str:
        return "; ".join(f'"{reason}"' for reason in reasons)
