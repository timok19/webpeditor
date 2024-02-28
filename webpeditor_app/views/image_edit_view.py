import logging
from types import NoneType

import cloudinary.uploader
from copy import copy

from cloudinary import CloudinaryImage
from django.core.handlers.wsgi import WSGIRequest
from django.http import (
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    HttpResponse,
)
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_service import (
    get_edited_image,
    get_image_file_instance,
    get_image_info,
    get_data_from_image_url,
    cut_image_name,
)

from webpeditor_app.services.other_services.session_service import get_session_key
from webpeditor_app.views.view_utils.get_user_data import (
    get_user_id_or_401,
    get_original_image_or_401,
)

logging.basicConfig(level=logging.INFO)


def create_and_save_edited_image(
    user_id: str, original_image: OriginalImage, session_key: str, request: WSGIRequest
) -> EditedImage | HttpResponsePermanentRedirect | HttpResponseRedirect:
    original_image_url = original_image.image_url
    image_name = original_image.image_name
    folder_path = f"{user_id}/edited/"

    cloudinary_parameters: dict = {
        "folder": folder_path,
        "use_filename": True,
        "filename_override": image_name,
        "unique_filename": False,
        "overwrite": True,
    }
    try:
        cloudinary_image: CloudinaryImage = cloudinary.uploader.upload_image(
            original_image_url, **cloudinary_parameters
        )
    except cloudinary.uploader.Error as e:
        logging.error(e)
        return redirect("ImageDoesNotExistView")

    edited_image_init = EditedImage(
        user_id=user_id,
        original_image=original_image,
        image_url=cloudinary_image.url,
        image_name=image_name,
        content_type=original_image.content_type,
        session_key=session_key,
        session_key_expiration_date=request.session.get_expiry_date(),
    )
    edited_image_init.save()

    return edited_image_init


@require_http_methods(["GET"])
def image_edit_view(
    request: WSGIRequest,
) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    session_key = get_session_key(request)

    user_id: str | HttpResponse = get_user_id_or_401(request)
    if isinstance(user_id, HttpResponse):
        return user_id

    original_image: OriginalImage | HttpResponse = get_original_image_or_401(
        request, user_id
    )
    if isinstance(original_image, HttpResponse):
        return original_image

    edited_image: EditedImage | None = get_edited_image(user_id)
    if isinstance(edited_image, NoneType) and isinstance(original_image, OriginalImage):
        edited_image = create_and_save_edited_image(
            user_id, original_image, session_key, request
        )
    elif isinstance(edited_image, NoneType):
        return render(request, "imageIsNotUploadedView.html", status=401)
    elif edited_image.image_url is None:
        return render(request, "imageIsNotUploadedView.html", status=401)

    edited_image_data = get_data_from_image_url(edited_image.image_url)
    if isinstance(edited_image_data, NoneType):
        return render(request, "imageIsNotUploadedView.html", status=401)

    image_info = get_image_info(copy(edited_image_data))
    edited_image_size = image_info[2]
    edited_image_resolution = image_info[3]
    edited_image_aspect_ratio = image_info[4]
    edited_image_exif_data = image_info[6]

    # Original image format description to show on FE
    original_image_data = get_data_from_image_url(original_image.image_url)
    original_image_file = get_image_file_instance(original_image_data)
    original_image_format = original_image_file.format.lower()
    original_image_format_description = original_image_file.format_description
    original_image_mode = original_image_file.mode
    original_image_name_with_extension = (
        f"{edited_image.image_name}.{original_image_format}"
    )

    context: dict = {
        "edited_image_url": edited_image.image_url,
        "edited_image_name_short": cut_image_name(
            original_image_name_with_extension, 20
        ),
        "edited_image_size": edited_image_size,
        "edited_image_resolution": edited_image_resolution,
        "edited_image_aspect_ratio": edited_image_aspect_ratio,
        "edited_image_format": original_image_format_description,
        "edited_image_mode": original_image_mode,
        "edited_image_exif_data": edited_image_exif_data,
        "edited_image_name_with_extension": original_image_name_with_extension,
        "edited_image_content_type": original_image.content_type,
    }

    original_image_file.close()

    return render(request, "imageEdit.html", context, status=200)
