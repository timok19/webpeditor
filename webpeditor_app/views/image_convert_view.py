from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor.settings import USER_ID_COOKIE
from webpeditor_app.models.database.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import convert_images
from webpeditor_app.services.other_services.session_service import update_session, create_user_id, \
    get_user_id
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


def post(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    response = redirect('ImageConvertView')

    if get_user_id(request) is None:
        user_id_signed = create_user_id()
        response.set_signed_cookie(USER_ID_COOKIE, user_id_signed, max_age=72000)

    user_id = get_user_id(request)

    image_form = ImagesToConvertForm(request.POST, request.FILES)
    if not image_form.is_valid():
        return redirect('ImageConvertView')

    images_files = request.FILES.getlist('images_to_convert')

    try:
        for image_file in images_files:
            validate_image_file_size(image_file)
    except ValidationError as errors:
        error_str = "".join(str(error) for error in errors)
        context: dict = {
            'form': image_form,
            'validation_error': error_str
        }

        return render(request, 'imageConvert.html', context)

    output_format = image_form.cleaned_data['output_format']

    converted_images_or_format_error = convert_images(images_files, output_format)
    if isinstance(converted_images_or_format_error, str):
        context: dict = {
            'form': image_form,
            'image_format_error': converted_images_or_format_error
        }

        return render(request, 'imageConvert.html', context)

    update_session(request=request, user_id=user_id)

    return response


def get(request: WSGIRequest):
    image_form = ImagesToConvertForm()
    converted_images_or_format_error = None

    context: dict = {
        'form': image_form,
        'converted_images': converted_images_or_format_error
    }

    return render(request, 'imageConvert.html', context)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_convert_view(request: WSGIRequest):
    if request.method == 'POST':
        response = post(request)
        return response

    elif request.method == 'GET':
        response = get(request)
        return response

    else:
        return HttpResponse(status=405)
