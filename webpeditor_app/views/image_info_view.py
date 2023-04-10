from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.image_services.image_service import \
    get_original_image, \
    format_image_file_name, \
    get_original_image_file_path, get_info_about_image
from webpeditor_app.services.other_services.session_service import update_image_editor_session, \
    get_user_id_from_session_store


@require_http_methods(['GET'])
def image_info_view(request) -> HttpResponse:
    user_id = get_user_id_from_session_store(request)
    if user_id is None:
        return redirect('ImageUploadView')

    original_image = get_original_image(user_id)
    if original_image is None:
        return redirect("ImageDoesNotExistView")

    if original_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")

    path_to_local_image: Path = get_original_image_file_path(user_id, original_image)

    result = get_info_about_image(path_to_local_image)

    if result is None:
        return redirect("ImageDoesNotExistView")
    else:
        image_format_description = result[0]
        image_size = result[1]
        image_resolution = result[2]
        image_aspect_ratio = result[3]
        image_mode = result[4]

    context: dict = {
        'original_image_url': original_image.original_image.url,
        'image_name': format_image_file_name(original_image.image_name),
        'image_format': image_format_description,
        'image_size': image_size,
        'image_resolution': image_resolution,
        'aspect_ratio': image_aspect_ratio,
        'image_mode': image_mode
    }

    update_image_editor_session(request=request, user_id=user_id)

    return render(request, 'imageInfo.html', context)
