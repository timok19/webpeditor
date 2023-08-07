from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def unauthorized_access_view(request: WSGIRequest):
    response = HttpResponse(status=401)
    response_message = "Unauthorized access"

    context = {
        "status_code": response.status_code,
        "response_message": response_message,
    }

    return render(request, "noContent.html", context, status=401)
