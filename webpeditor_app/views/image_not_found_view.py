from http import HTTPStatus
from typing import Any
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView


class ImageNotFoundView(TemplateView):
    template_name = "webpeditor_app/content-not-found.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        context.update(message="Image Not Found")
        return self.render_to_response(context, status=HTTPStatus.NOT_FOUND)
