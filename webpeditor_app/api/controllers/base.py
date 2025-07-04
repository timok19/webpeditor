from typing import Optional

from django.http import HttpRequest, HttpResponse
from ninja_extra import ControllerBase as FactoryControllerBase
from ninja_extra.context import RouteContext


class ControllerBase(FactoryControllerBase):
    @property
    def request(self) -> HttpRequest:
        context = self.__validate_context(self.context)
        return self.__validate_request(context.request)

    @property
    def response(self) -> HttpResponse:
        context = self.__validate_context(self.context)
        return self.__validate_response(context.response)

    @staticmethod
    def __validate_context(context: Optional[RouteContext]) -> RouteContext:
        if context is None:
            raise ValueError("Route context is required.")
        return context

    @staticmethod
    def __validate_request(request: Optional[HttpRequest]) -> HttpRequest:
        if request is None:
            raise ValueError("Request is required.")
        return request

    @staticmethod
    def __validate_response(response: Optional[HttpResponse]) -> HttpResponse:
        if response is None:
            raise ValueError("Response is required.")
        return response
