import os
from decimal import Decimal, ROUND_UP
from pathlib import Path

from PIL import Image as PilImage
from PIL.Image import Image as ImageClass
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.other_services.session_service import update_session


def get_original_image(user_id: str) -> OriginalImage | None:
    try:
        return OriginalImage.objects.filter(user_id=user_id).first()
    except OriginalImage.DoesNotExist:
        return None


def get_image_local_file(path_to_local_image: Path) -> ImageClass | None:
    try:
        return PilImage.open(path_to_local_image)
    except (FileExistsError, FileNotFoundError):
        return None


def format_image_name(image_name: str) -> str:
    basename, ext = os.path.splitext(image_name)
    if len(basename) > 20:
        basename = basename[:17] + "..."
    return basename + ext


def format_image_size(path_to_local_image: Path) -> str:
    size = round(os.path.getsize(path_to_local_image) / 1024, 2)
    if size > 1000:
        size /= 1024
        return "{} MB".format(round(size, 2))
    return "{} KB".format(size)


@require_http_methods(['GET'])
def image_info_view(request) -> HttpResponse:
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('UploadImageView')

    uploaded_image = get_original_image(user_id)
    if uploaded_image is None:
        return redirect("ImageDoesNotExistView")

    if uploaded_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")

    path_to_local_image = settings.MEDIA_ROOT / uploaded_image.user_id / uploaded_image.image_name
    image_local_file = get_image_local_file(path_to_local_image)
    if image_local_file is None:
        return redirect("ImageDoesNotExistView")

    aspect_ratio: Decimal = Decimal(image_local_file.width / image_local_file.height) \
        .quantize(Decimal('.1'), rounding=ROUND_UP)

    context: dict = {
        'uploaded_image_url_to_fe': uploaded_image.original_image_url.url,
        'image_format': image_local_file.format,
        'image_resolution': f"{image_local_file.width}px ⨯ {image_local_file.height}px",
        'image_name': format_image_name(uploaded_image.image_name),
        'aspect_ratio': aspect_ratio,
        'image_size': format_image_size(path_to_local_image),
    }

    update_session(request=request, user_id=user_id)
    return render(request, 'imageInfo.html', context)
