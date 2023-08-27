from django.core.handlers.asgi import ASGIRequest
from django.views.generic import TemplateView
from django.http.response import HttpResponseForbidden


class UnauthorizedAccessView(TemplateView):
    template_name = "noContent.html"
    http_method_names = ["get"]
    extra_context = {
        "status_code": HttpResponseForbidden.status_code,
        "response_message": "Not found",
    }

    def get(self, request: ASGIRequest, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
