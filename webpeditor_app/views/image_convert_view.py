from django.core.exceptions import ValidationError, TooManyFilesSent
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import convert_images
from webpeditor_app.services.other_services.session_service import \
    add_user_id_into_session_store, \
    update_session
from webpeditor_app.services.validators.image_file_validator import \
    validate_image_files, \
    validate_number_of_image_files


def post(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    user_id = add_user_id_into_session_store(request)

    image_form = ImagesToConvertForm(request.POST, request.FILES)
    if not image_form.is_valid():
        return redirect('ImageConvertView')

    image_files = request.FILES.getlist('images_to_convert')

    try:
        validate_number_of_image_files(image_files)
    except TooManyFilesSent as error_str:
        context: dict = {
            'form': image_form,
            'validation_error': error_str
        }

        return render(request, 'imageConvert.html', context)

    try:
        validate_image_files(image_files)
    except ValidationError as errors:
        error_str = "".join(str(error) for error in errors)
        context: dict = {
            'form': image_form,
            'validation_error': error_str
        }

        return render(request, 'imageConvert.html', context)

    output_format = image_form.cleaned_data['output_format']

    converted_images = convert_images(image_files, output_format)

    if isinstance(converted_images, str):
        format_error = converted_images
        context: dict = {
            'form': image_form,
            'image_format_error': format_error
        }
    else:
        context: dict = {
            'form': image_form,
            'converted_images': converted_images
        }

    update_session(request=request, user_id=user_id)

    return render(request, 'imageConvert.html', context)


def get(request: WSGIRequest):
    image_form = ImagesToConvertForm()
    converted_images = None

    context: dict = {
        'form': image_form,
        'converted_images': converted_images
    }

    return render(request, 'imageConvert.html', context)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_convert_view(request: WSGIRequest):
    if request.method == 'POST':
        response = post(request)
        return response

    else:
        response = get(request)
        return response
