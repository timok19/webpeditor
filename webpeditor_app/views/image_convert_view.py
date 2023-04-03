from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from webpeditor_app.models.database.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import convert_images
from webpeditor_app.services.other_services.session_service import update_session
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size
from webpeditor_app.views.image_edit_view import get_user_id


def image_convert_view(request: WSGIRequest):
    user_id = get_user_id(request)

    if request.method == 'POST':
        image_form = ImagesToConvertForm(request.POST, request.FILES)
        if not image_form.is_valid():
            return redirect('ImageConvertView')

        images_files = request.FILES.getlist('images_to_convert')

        try:
            for image_file in images_files:
                validate_image_file_size(image_file)
        except ValidationError as errors:
            error_str = "".join(str(error) for error in errors)
            return render(request, 'imageConvert.html', {'form': image_form, 'validation_error': error_str})

        output_format = image_form.cleaned_data['output_format']

        converted_images = convert_images(images_files, output_format)
        if isinstance(converted_images, str):
            return render(request, 'imageConvert.html', {'form': image_form, 'image_format_error': converted_images})

    else:
        image_form = ImagesToConvertForm()
        converted_images = None

    update_session(request=request, user_id=user_id)

    return render(request, 'imageConvert.html', {'form': image_form, 'converted_images': converted_images})
