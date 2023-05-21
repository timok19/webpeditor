import logging
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.forms.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_service import get_converted_image
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id

logging.basicConfig(level=logging.INFO)


@requires_csrf_token
@require_http_methods(['GET'])
def image_convert_view(request: WSGIRequest):
    image_form = ImagesToConvertForm()
    user_id = get_unsigned_user_id(request)

    context = {
        'form': image_form,
        'error': request.session.get('error_message'),
        'converted_images':
            request.session.get('converted_images')
            if get_converted_image(user_id)
            else None
    }
    return render(request, 'imageConvert.html', context, status=200)

