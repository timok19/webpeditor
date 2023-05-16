from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import requires_csrf_token, csrf_protect
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from webpeditor_app.forms.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import run_conversion_task
from webpeditor_app.services.other_services.session_service import (update_session,
                                                                    get_unsigned_user_id,
                                                                    add_signed_user_id_to_session_store,
                                                                    set_session_expiry)

from webpeditor_app.services.validators.image_file_validator import validate_images


@requires_csrf_token
@csrf_protect
@require_http_methods(['POST'])
def image_convert_api(request: WSGIRequest):
    if request.method == 'POST':
        user_id = get_unsigned_user_id(request)
        if user_id is None:
            add_signed_user_id_to_session_store(request)
            user_id = get_unsigned_user_id(request)

        set_session_expiry(request, 900)

        image_form = ImagesToConvertForm(request.POST, request.FILES)
        if not image_form.is_valid():
            request.session['error_message'] = "One or many unknown file format(s)"
            request.session['converted_images'] = None
            return HttpResponseRedirect(reverse('ImageConvertView'), status=400)

        image_files = request.FILES.getlist('images_to_convert')

        # Validate image size
        if isinstance(image_files, list) and validate_images(request, image_files) is False:
            return HttpResponseRedirect(reverse('ImageConvertView'), status=500)

        output_format: str = request.POST.get('output_format')
        quality: str = request.POST.get('quality')

        try:
            converted_images: list = run_conversion_task(user_id, request, image_files, int(quality), output_format)
            update_session(request=request, user_id=user_id)
            request.session.pop('error_message', None)
            request.session.pop('converted_images', None)
            request.session['converted_images'] = converted_images

            return HttpResponseRedirect(reverse('ImageConvertView'))

        except Exception as e:
            response = HttpResponse()
            response.content = str(e)
            response.status_code = 500

            return response
