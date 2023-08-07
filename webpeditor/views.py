from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.conf import settings


def service_worker(request: WSGIRequest):
    sw_path = settings.BASE_DIR / "static" / "js" / "sw.js"

    return HttpResponse(open(sw_path).read(), content_type="application/javascript")
