from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def no_content_view(request: WSGIRequest):
    response = HttpResponse(status=404)
    response_message = 'Not found'

    context = {
        'status_code': response.status_code,
        'response_message': response_message
    }

    return render(request, 'noContent.html', context)
