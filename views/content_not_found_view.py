from http import HTTPStatus
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView


class ContentNotFoundView(TemplateView):
    template_name = "webpeditor_app/content-not-found.html"
    extra_context = {"message": "Content Not Found"}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.render_to_response(self.get_context_data(**kwargs), status=HTTPStatus.NOT_FOUND)
