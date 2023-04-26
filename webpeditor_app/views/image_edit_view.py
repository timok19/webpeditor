import logging

import cloudinary.uploader
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_service import \
    get_original_image, \
    get_edited_image, \
    get_image_file_instance, \
    get_info_about_image, get_data_from_image_url
from webpeditor_app.services.other_services.session_service import \
    update_session, \
    get_session_id, \
    get_user_id_from_session_store
from webpeditor_app.views.image_info_view import image_name_shorter

logging.basicConfig(level=logging.INFO)


def create_and_save_edited_image(user_id: str,
                                 original_image: OriginalImage,
                                 session_key: str,
                                 request: WSGIRequest) -> EditedImage:

    original_image_url = original_image.image_url
    new_edited_image_name = original_image.image_name
    folder_path = f"{user_id}/edited/"

    cloudinary_parameters: dict = {
        "folder": folder_path,
        "use_filename": True,
        "filename_override": new_edited_image_name,
        "overwrite": True
    }
    cloudinary_image = cloudinary.uploader.upload_image(original_image_url, **cloudinary_parameters)

    edited_image_init = EditedImage(
        user_id=user_id,
        image_url=cloudinary_image.url,
        image_name=new_edited_image_name,
        content_type=original_image.content_type,
        session_id=session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        original_image=original_image
    )
    edited_image_init.save()

    return edited_image_init


def get(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    user_id = get_user_id_from_session_store(request)
    if user_id is None:
        return redirect('ImageDoesNotExistView')

    original_image = get_original_image(user_id)
    if original_image is None:
        return redirect("ImageDoesNotExistView")

    if original_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")

    session_key = get_session_id(request)

    edited_image = get_edited_image(user_id)
    if edited_image and original_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")
    elif edited_image is None and original_image.user_id == user_id:
        edited_image = create_and_save_edited_image(user_id, original_image, session_key, request)

    original_image_data = get_data_from_image_url(edited_image.image_url)
    if original_image_data is None:
        return redirect("ImageDoesNotExistView")

    image_info = get_info_about_image(original_image_data)
    edited_image_format = image_info[1]
    edited_image_size = image_info[2]
    edited_image_resolution = image_info[3]
    edited_image_aspect_ratio = image_info[4]
    edited_image_mode = image_info[5]
    edited_image_exif_data = image_info[6]
    edited_image_metadata = image_info[7]

    # Original image format description to show on FE
    original_image_data = get_data_from_image_url(original_image.image_url)
    if original_image_data is None:
        return redirect("ImageDoesNotExistView")

    original_image_file = get_image_file_instance(original_image_data)
    original_image_format_description = original_image_file.format_description

    edited_image_name_with_extension = f"{edited_image.image_name}.{edited_image_format}"

    context: dict = {
        'edited_image_url': edited_image.image_url,
        'edited_image_name_short': image_name_shorter(edited_image_name_with_extension),
        'edited_image_size': edited_image_size,
        'edited_image_resolution': edited_image_resolution,
        'edited_image_aspect_ratio': edited_image_aspect_ratio,
        'edited_image_format': original_image_format_description,
        'edited_image_mode': edited_image_mode,
        'edited_image_exif_data': edited_image_exif_data,
        'edited_image_metadata': edited_image_metadata,
        'edited_image_name_with_extension': edited_image_name_with_extension,
        'edited_image_content_type': edited_image.content_type
    }

    original_image_file.close()

    update_session(request=request, user_id=user_id)

    return render(request, 'imageEdit.html', context)


@requires_csrf_token
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    if request.method == "GET":
        response = get(request)
        return response
    else:
        return HttpResponse(status=405)
