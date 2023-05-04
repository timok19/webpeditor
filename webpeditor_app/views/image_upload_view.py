import logging
from typing import Tuple

import cloudinary.uploader
import cloudinary.api

from PIL import Image as PilImage

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor.settings import MAX_IMAGE_FILE_SIZE
from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.api_services.cloudinary_service import delete_cloudinary_original_and_edited_images
from webpeditor_app.services.image_services.image_service import get_original_image, get_image_file_name
from webpeditor_app.utils.text_utils import replace_with_underscore
from webpeditor_app.services.other_services.session_service import (update_session,
                                                                    get_unsigned_user_id,
                                                                    set_session_expiry,
                                                                    add_signed_user_id_to_session_store)

logging.basicConfig(level=logging.INFO)


def clean_up_previous_images(user_id: str):
    previous_original_image: OriginalImage | None = get_original_image(user_id)
    if isinstance(previous_original_image, OriginalImage):
        previous_original_image.delete()

    delete_cloudinary_original_and_edited_images(user_id)


def upload_original_image_to_cloudinary(image: InMemoryUploadedFile, user_id: str) -> Tuple[str, str]:
    folder_path: str = f"{user_id}/"

    image_name: str = get_image_file_name(str(image.name))
    image_name_after_re: str = replace_with_underscore(image_name)
    new_original_image_name: str = f"webpeditor_{image_name_after_re}"

    cloudinary_parameters: dict = {
        "folder": folder_path,
        "use_filename": True,
        "unique_filename": False,
        "filename_override": new_original_image_name,
        "overwrite": True
    }
    cloudinary_image = cloudinary.uploader.upload_image(image, **cloudinary_parameters)

    return cloudinary_image.url, new_original_image_name


def check_image_existence(request: WSGIRequest) -> bool:
    is_image_exist = True
    user_id = get_unsigned_user_id(request)

    original_image = get_original_image(user_id)
    if original_image is None:
        is_image_exist = False
        return is_image_exist

    return is_image_exist


def post(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    user_id = get_unsigned_user_id(request)
    if user_id is None:
        add_signed_user_id_to_session_store(request)
        user_id = get_unsigned_user_id(request)

    set_session_expiry(request, 900)

    clean_up_previous_images(user_id)

    if 'original_image_form' not in request.FILES:
        is_image_exist = check_image_existence(request)
        context: dict = {
            'error': 'No image file was provided.',
            'is_image_exist': is_image_exist
        }
        return render(request, 'imageUpload.html', context)

    uploaded_original_image_file: InMemoryUploadedFile = request.FILES['original_image_form']
    image = PilImage.open(uploaded_original_image_file)

    are_image_dimensions_more: bool = image.width > 2500 or image.height > 2500
    is_image_file_size_more: bool = uploaded_original_image_file.size > MAX_IMAGE_FILE_SIZE

    if is_image_file_size_more or are_image_dimensions_more:
        f'Image should not exceed {MAX_IMAGE_FILE_SIZE / 1_000_000} MB'
        if is_image_file_size_more:
            error = f'Image should not exceed {MAX_IMAGE_FILE_SIZE / 1_000_000} MB'
        else:
            error = f'Image dimensions should not be more than 2500x2500px'

        is_image_exist = check_image_existence(request)
        context: dict = {
            'error': error,
            'is_image_exist': is_image_exist
        }
        return render(request, 'imageUpload.html', context)

    uploaded_original_image_file.seek(0)
    cloudinary_image_url, new_image_name = upload_original_image_to_cloudinary(
        uploaded_original_image_file,
        user_id
    )

    original_image = OriginalImage(
        user_id=user_id,
        image_name=new_image_name,
        content_type=uploaded_original_image_file.content_type,
        image_url=cloudinary_image_url,
        session_key=request.session.session_key,
        session_key_expiration_date=request.session.get_expiry_date()
    )
    original_image.save()
    image.close()

    update_session(request=request, user_id=user_id)

    return redirect('ImageInfoView')


def get(request: WSGIRequest) -> HttpResponse:
    form = OriginalImageForm()
    is_image_exist = check_image_existence(request)
    context: dict = {
        'form': form,
        'is_image_exist': is_image_exist
    }

    return render(request, 'imageUpload.html', context, status=200)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_upload_view(
        request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    if request.method == 'POST':
        response = post(request)
        return response

    elif request.method == 'GET':
        response = get(request)
        return response

    else:
        return HttpResponse(status=405)
