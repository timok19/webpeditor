from typing import Any, Callable, Final, final

from anydi_django import container
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

        if isinstance(response, HttpResponse) and self.__is_error(response):
            self.__process(request, response)

        return response

    @staticmethod
    def __is_error(response: HttpResponse) -> bool:
        return Enumerable[int](codes_4xx).union(codes_5xx).any(lambda status_code: response.status_code == status_code)

    def __process(self, request: HttpRequest, response: HttpResponse) -> None:
        return (
            self.__validate_json(request, response)
            .map(lambda error: self.__logger.request_error(request, error.model_dump_json()))
            .to_optional()
        )

    def __validate_json(self, request: HttpRequest, response: HttpResponse) -> Option[HTTPResult[Any]]:
        try:
            return Option[HTTPResult[Any]].Some(HTTPResult[Any].model_validate_json(response.content))
        except ValidationError:
            return Option[HTTPResult[Any]].Nothing()
        except Exception as exception:
            reason = response.content.decode(response.charset or "utf-8")
            self.__logger.request_exception(request, exception, f"Unhandled error. Reason: '{reason}'")
            return Option[HTTPResult[Any]].Nothing()
