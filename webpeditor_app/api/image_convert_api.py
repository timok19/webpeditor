from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from webpeditor_app.models.database.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import convert_and_save_images
from webpeditor_app.services.other_services.session_service import update_session, get_unsigned_user_id, \
    add_signed_user_id_to_session_store, set_session_expiry
from webpeditor_app.services.validators.image_file_validator import validate_images


@requires_csrf_token
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
            request.session.pop('error_message', None)
            request.session['error_message'] = f"This field is required"
            return HttpResponseRedirect(reverse('ImageConvertView'))

        image_files = request.FILES.getlist('images_to_convert')

        # Validate image size
        if validate_images(request, image_files) is False:
            return HttpResponseRedirect(reverse('ImageConvertView'))

        output_format = request.POST.get('output_format')

        try:
            converted_images = convert_and_save_images(user_id, request, image_files, output_format)
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
