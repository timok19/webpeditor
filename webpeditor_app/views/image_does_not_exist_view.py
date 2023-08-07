from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def image_does_not_exist_view(request: WSGIRequest):
    response = HttpResponse(status=404)
    response_message = "Image not found"

    content: dict = {
        "status_code": response.status_code,
        "response_message": response_message,
    }

    return render(request, "imageDoesNotExist.html", content, status=404)
