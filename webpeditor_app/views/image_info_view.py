from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.image_services.image_service import \
    get_original_image, \
    get_image_file_instance, \
    format_image_file_name, \
    get_image_file_size, \
    get_image_aspect_ratio, \
    get_original_image_file_path
from webpeditor_app.services.other_services.session_service import update_image_editor_session, get_user_id_from_session_store


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

    image_local_file = get_image_file_instance(path_to_local_image)
    if image_local_file is None:
        return redirect("ImageDoesNotExistView")

    context: dict = {
        'original_image_url': original_image.original_image.url,
        'image_format': image_local_file.format,
        'image_resolution': f"{image_local_file.width}px ⨯ {image_local_file.height}px",
        'image_name': format_image_file_name(original_image.image_name),
        'aspect_ratio': get_image_aspect_ratio(image_local_file),
        'image_size': get_image_file_size(image_local_file),
    }

    update_image_editor_session(request=request, user_id=user_id)

    return render(request, 'imageInfo.html', context)
