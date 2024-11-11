from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def image_does_not_exist_view(request: WSGIRequest):
    return render(request, "webpeditor_app/imageDoesNotExist.html", context={"response_message": "Image not found"}, status=404)
