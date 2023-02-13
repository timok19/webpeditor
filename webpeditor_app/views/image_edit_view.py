from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def image_edit_view(request: WSGIRequest):

    return render(request, 'imageEdit.html')
