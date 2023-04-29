from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import ImagesToConvertForm


@requires_csrf_token
@require_http_methods(['GET'])
def image_convert_view(request: WSGIRequest):
    if request.method == 'GET':
        image_form = ImagesToConvertForm()
        error_message = request.session.get('error_message')
        converted_images = request.session.get('converted_images')

        context = {
            'form': image_form,
            'error': error_message,
            'converted_images': converted_images
        }

        return render(request, 'imageConvert.html', context, status=200)
