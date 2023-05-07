from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def about_view(request: WSGIRequest) -> HttpResponse:
    return render(request, "about.html")
