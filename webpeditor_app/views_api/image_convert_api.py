from django.core.exceptions import ValidationError, TooManyFilesSent
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from webpeditor_app.models.database.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import convert_images
from webpeditor_app.services.validators.image_file_validator import \
    validate_image_files, \
    validate_number_of_image_files
from webpeditor_app.services.other_services.session_service import get_or_add_user_id, update_session


@requires_csrf_token
@require_http_methods(['POST'])
def image_convert_api(request: WSGIRequest):
    if request.method == 'POST':
        user_id = get_or_add_user_id(request)

        image_form = ImagesToConvertForm(request.POST, request.FILES)
        if not image_form.is_valid():
            return redirect('ImageConvertView')

        image_files = request.FILES.getlist('images_to_convert')

        try:
            validate_number_of_image_files(image_files)
        except TooManyFilesSent as error_str:
            request.session.pop('validation_file_number_error', None)
            request.session['validation_file_number_error'] = str(error_str)

            return HttpResponseRedirect(reverse('ImageConvertView'))

        try:
            validate_image_files(image_files)
        except ValidationError as errors:
            error_str = "".join(str(error) for error in errors)
            request.session.pop('validation_file_size_error', None)
            request.session['validation_file_size_error'] = error_str

            return HttpResponseRedirect(reverse('ImageConvertView'))

        output_format = request.POST.get('output_format')

        try:
            converted_images = convert_images(image_files, output_format)
            update_session(request=request, user_id=user_id)

            request.session.pop('converted_images', None)
            request.session['converted_images'] = converted_images

            return HttpResponseRedirect(reverse('ImageConvertView'))

        except Exception as e:
            response = HttpResponse(content=str(e), status=500)

            return response
