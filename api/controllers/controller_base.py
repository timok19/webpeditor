from http.client import HTTPException
from typing import Optional

from django.http import HttpRequest
from ninja_extra import ControllerBase as NinjaControllerBase
from ninja_extra.context import RouteContext


class ControllerBase(NinjaControllerBase):
    @property
    def http_request(self) -> HttpRequest:
        context = self.__validate_context(self.context)
        request = self.__validate_request(context.request)
        return request

    @staticmethod
    def __validate_context(context: Optional[RouteContext]) -> RouteContext:
        if context is None:
            raise HTTPException(f"{RouteContext.__name__} cannot be None!")
        return context

    @staticmethod
    def __validate_request(request: Optional[HttpRequest]) -> HttpRequest:
        if request is None:
            raise HTTPException(f"{HttpRequest.__name__} cannot be None!")
        return request
