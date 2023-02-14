from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import redirect, render

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.folder_name_with_session_id import create_folder_name_with_session_id
from webpeditor_app.services.image_services.re_for_file_name import replace_with_underscore
from webpeditor_app.services.image_services.session_id_to_db import set_session_expiry, update_session
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


def image_upload_view(request: WSGIRequest):
    set_session_expiry(request)

    if request.method == 'POST':
        previous_image = OriginalImage.objects.filter(session_id=request.session.session_key).first()
        if previous_image:
            default_storage.delete(previous_image.original_image_url.name)
            previous_image.delete()


        image_form = OriginalImageForm(request.POST, request.FILES)
        user_folder: Path = create_folder_name_with_session_id(session_id=request.session.session_key)

        if not image_form.is_valid():
            return redirect('UploadImageView')

        image: UploadedFile = image_form.cleaned_data['image']

        try:
            validate_image_file_size(image)
        except ValidationError as errors:
            error_str = ""
            for error in errors:
                error_str += str(error)

            return render(request, 'imageUpload.html', {'form': image_form, 'validation_error': error_str})

        image_name_after_re: str = replace_with_underscore(image.name)

        uploaded_image_path_to_local = user_folder / image_name_after_re
        default_storage.save(uploaded_image_path_to_local, image)

        uploaded_image_path_to_db = str(request.session.session_key + '/' + image_name_after_re)
        original_image_object = OriginalImage(image_file=image_name_after_re,
                                              content_type=image.content_type,
                                              original_image_url=uploaded_image_path_to_db,
                                              session_id=request.session.session_key)

        original_image_object.save()

        update_session(request.session.session_key)

        return redirect('ImageInfoView')

    else:
        image_form = OriginalImageForm()
        original_image = OriginalImage.objects.filter(session_id=request.session.session_key).first()

    return render(request, 'imageUpload.html', {'form': image_form, 'original_image': original_image})
