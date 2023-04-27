import logging
from typing import Tuple

import cloudinary.uploader
import cloudinary.api
from django.core.exceptions import PermissionDenied

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor.settings import MAX_IMAGE_FILE_SIZE
from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.api_services.cloudinary_service import delete_user_folder_with_content
from webpeditor_app.services.image_services.image_service import get_original_image, get_file_name
from webpeditor_app.services.image_services.text_utils import replace_with_underscore
from webpeditor_app.services.other_services.session_service import \
    update_session, \
    get_unsigned_user_id, \
    set_session_expiry, add_signed_user_id

logging.basicConfig(level=logging.INFO)


def clean_up_previous_images(user_id: str):
    previous_original_image = get_original_image(user_id)
    if previous_original_image.session_key is not None:
        previous_original_image.delete()

    delete_user_folder_with_content(user_id)


def upload_original_image_to_cloudinary(image: InMemoryUploadedFile, user_id: str) -> Tuple[str, str]:
    folder_path: str = user_id

    image_name: str = get_file_name(str(image.name))
    image_name_after_re: str = replace_with_underscore(image_name)
    new_original_image_name: str = f"webpeditor_{image_name_after_re}"

    cloudinary_parameters: dict = {
        "folder": folder_path,
        "use_filename": True,
        "filename_override": new_original_image_name,
        "overwrite": True,
    }
    cloudinary_image = cloudinary.uploader.upload_image(image, **cloudinary_parameters)

    return str(cloudinary_image.url), new_original_image_name


def check_image_existence(request: WSGIRequest) -> bool:
    is_image_exist = True
    user_id = get_unsigned_user_id(request)

    original_image = get_original_image(user_id)
    if original_image is None or original_image.image_url == "":
        is_image_exist = False
        return is_image_exist

    return is_image_exist


def post(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    set_session_expiry(request, 900)
    user_id = get_unsigned_user_id(request)

    original_image = get_original_image(user_id)
    if original_image is None:
        raise PermissionDenied("You do not have permission to view this image.")

    clean_up_previous_images(user_id)

    uploaded_original_image_file: InMemoryUploadedFile = request.FILES['original_image_form']
    if uploaded_original_image_file.size > MAX_IMAGE_FILE_SIZE:
        is_image_exist = check_image_existence(request)
        context: dict = {
            'error': f'Image should not exceed {MAX_IMAGE_FILE_SIZE / 1_000_000} MB',
            'is_image_exist': is_image_exist
        }
        return render(request, 'imageUpload.html', context)

    image_url, new_image_name = upload_original_image_to_cloudinary(uploaded_original_image_file, user_id)

    values_to_update: dict = {
        "image_name": new_image_name,
        "content_type": uploaded_original_image_file.content_type,
        "image_url": image_url,
        "session_key": request.session.session_key,
        "session_key_expiration_date": request.session.get_expiry_date()
    }
    OriginalImage.objects.filter(user_id=user_id).update(**values_to_update)

    update_session(request=request, user_id=user_id)

    return redirect('ImageInfoView')


def get(request: WSGIRequest) -> HttpResponse:
    if "user_id" not in request.session:
        add_signed_user_id(request)

    form = OriginalImageForm()
    is_image_exist = check_image_existence(request)
    context: dict = {
        'form': form,
        'is_image_exist': is_image_exist
    }

    return render(request, 'imageUpload.html', context)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_upload_view(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    if request.method == 'POST':
        response = post(request)
        return response

    elif request.method == 'GET':
        response = get(request)
        return response

    else:
        return HttpResponse(status=405)
