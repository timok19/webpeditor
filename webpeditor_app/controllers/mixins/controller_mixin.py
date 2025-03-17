from django.http import HttpRequest, HttpResponse
from ninja_extra.context import RouteContext
from typing import Optional


class ControllerMixin:
    @classmethod
    def get_request(cls, context: Optional[RouteContext]) -> HttpRequest:
        ctx = cls.__validate_context(context)
        return cls.__validate_request(ctx.request)

    @classmethod
    def get_response(cls, context: Optional[RouteContext]) -> HttpResponse:
        ctx = cls.__validate_context(context)
        return cls.__validate_response(ctx.response)

    @classmethod
    def __validate_request(cls, request: Optional[HttpRequest]) -> HttpRequest:
        if request is None:
            raise ValueError("Request is required.")
        return request

    @classmethod
    def __validate_context(cls, context: Optional[RouteContext]) -> RouteContext:
        if context is None:
            raise ValueError("Route context is required.")
        return context

    @classmethod
    def __validate_response(cls, response: Optional[HttpResponse]) -> HttpResponse:
        if response is None:
            raise ValueError("Response is required.")
        return response
