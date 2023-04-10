from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import ImagesToConvertForm


@requires_csrf_token
@require_http_methods(['GET'])
def image_convert_view(request: WSGIRequest):
    image_form = ImagesToConvertForm()

    validation_file_size_error = request.session.pop('validation_file_size_error', None)
    if validation_file_size_error:
        context: dict = {
            'form': image_form,
            'validation_file_size_error': validation_file_size_error
        }

        return render(request, 'imageConvert.html', context)

    converted_images = request.session.get('converted_images')
    context = {
        'form': image_form,
        'validation_file_size_error': validation_file_size_error,
        'converted_images': converted_images
    }

    return render(request, 'imageConvert.html', context)
