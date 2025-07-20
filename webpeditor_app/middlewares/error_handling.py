from typing import Any, Callable, Final, final, cast

from anydi.ext.django import container
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from expression import Option
from ninja.responses import codes_4xx, codes_5xx
from pydantic import ValidationError
from types_linq import Enumerable

from webpeditor_app.api.controllers.schemas import HTTPResult
from webpeditor_app.core.abc.logger_abc import LoggerABC


@final
class ErrorHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.__logger: Final[LoggerABC] = container.resolve(LoggerABC)
        self.get_response: Callable[[HttpRequest], HttpResponseBase] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        return self.__process(request, cast(HttpResponse, response)) if self.__is_error_response(response) else response

    @staticmethod
    def __is_error_response(response: HttpResponseBase) -> bool:
        return isinstance(response, HttpResponse) and Enumerable(codes_4xx).union(codes_5xx).any(lambda code: response.status_code == code)

    def __process(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        validation_result = self.__validate_json(request, response)

        if validation_result.is_some():
            self.__logger.log_request_error(request, validation_result.some.model_dump_json())

        return response

    def __validate_json(self, request: HttpRequest, response: HttpResponse) -> Option[HTTPResult[Any]]:
        try:
            return Option[HTTPResult[Any]].Some(HTTPResult[Any].model_validate_json(response.content))
        except ValidationError:
            return Option[HTTPResult[Any]].Nothing()
        except Exception as exception:
            reason = response.content.decode(response.charset or "utf-8")
            self.__logger.log_request_exception(request, exception, f"Unhandled error. Reason: '{reason}'")
            return Option[HTTPResult[Any]].Nothing()
