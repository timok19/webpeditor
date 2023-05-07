from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def contact_view(request: WSGIRequest) -> HttpResponse:
    return render(request, "contact.html")
