from pathlib import Path
from PIL import Image
import os

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render

from webpeditor import settings
from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.folder_name_with_session_id import create_folder_name_with_session_id
from webpeditor_app.services.image_services.re_for_file_name import replace_with_underscore
from webpeditor_app.services.image_services.session_id_to_db import set_session_expiry, update_session
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


def upload_image_view(request: WSGIRequest):
    set_session_expiry(request)

    if request.method != 'POST':
        image_form = OriginalImageForm()
    else:
        image_form = OriginalImageForm(request.POST, request.FILES)

        if not image_form.is_valid():
            return redirect('UploadImageView')
        else:
            user_folder: Path = create_folder_name_with_session_id(request.session.session_key)
            previous_image = OriginalImage.objects.filter(session_id=request.session.session_key).first()

            if previous_image:
                default_storage.delete(previous_image.original_image_url.name)
                previous_image.delete()

            image: UploadedFile = image_form.cleaned_data['image']

            try:
                validate_image_file_size(image)
            except ValidationError as error:
                print("Error: " + str(error))

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

    return render(request, 'imageUpload.html', {'form': image_form})


def show_image_info_view(request: WSGIRequest):
    uploaded_image_url = None
    uploaded_image_resolution = None
    uploaded_image_format = None
    uploaded_image_image_name = None
    uploaded_image_aspect_ratio = None
    uploaded_image_size = None

    if request.method == 'GET':
        uploaded_image = OriginalImage.objects.filter(session_id=request.session.session_key).first()

        if not uploaded_image:
            return redirect("ImageDoesNotExist")

        uploaded_image_url = uploaded_image.original_image_url.url
        path_to_local_image: Path = settings.MEDIA_ROOT / request.session.session_key / uploaded_image.image_file

        image_local_file = Image.open(path_to_local_image)

        # Image format
        uploaded_image_format = ".{}".format(image_local_file.format)

        # Image size
        uploaded_image_resolution = "{}px * {}px".format(image_local_file.size[0], image_local_file.size[1])

        # Image name
        basename, ext = os.path.splitext(uploaded_image.image_file)
        if len(basename) > 20:
            basename = basename[:17] + "..."
            uploaded_image_image_name = basename + ext
        else:
            uploaded_image_image_name = uploaded_image.image_file

        # Image aspect ratio
        uploaded_image_aspect_ratio = round(image_local_file.width / image_local_file.height, 1)

        # Image size
        size = round(os.path.getsize(path_to_local_image) / 1024)
        uploaded_image_size = "{} KB".format(size)

        if size > 1000:
            size /= 1024
            uploaded_image_size = "{} MB".format(round(size))

        update_session(request.session.session_key)

    return render(request, 'imageInfo.html', {'uploaded_image_url': uploaded_image_url,
                                              'session_id': request.session.session_key,
                                              'image_format': uploaded_image_format,
                                              'image_resolution': uploaded_image_resolution,
                                              'image_name': uploaded_image_image_name,
                                              'aspect_ratio': uploaded_image_aspect_ratio,
                                              'image_size': uploaded_image_size})


def image_does_not_exist_view(request: WSGIRequest):
    response = HttpResponse(status=404)
    return render(request, 'imageDoesNotExist.html', {'status_code': response.status_code})
