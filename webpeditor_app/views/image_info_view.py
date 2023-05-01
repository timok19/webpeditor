import logging

from _decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.image_services.image_service import \
    get_original_image, image_name_shorter, get_image_info, get_data_from_image_url

from webpeditor_app.services.other_services.session_service import \
    update_session, get_unsigned_user_id

logging.basicConfig(level=logging.INFO)


@require_http_methods(['GET'])
def image_info_view(request) -> HttpResponse:
    user_id = get_unsigned_user_id(request)
    if user_id is None:
        return render(request, "imageIsNotUploadedView.html", status=401)

    original_image = get_original_image(user_id)
    if original_image is None or original_image.user_id != user_id:
        return render(request, "imageIsNotUploadedView.html", status=401)

    image_data = get_data_from_image_url(original_image.image_url)
    if image_data is None:
        return redirect("ImageDoesNotExistView")

    # Image info taken from file
    image_info = get_image_info(image_data)

    image_format_description: str = image_info[0]
    image_format: str = image_info[1]
    image_size: str = image_info[2]
    image_resolution: str = image_info[3]
    image_aspect_ratio: Decimal = image_info[4]
    image_mode: str = image_info[5]

    context: dict = {
        'original_image_url': original_image.image_url,
        'image_name': image_name_shorter(f"{original_image.image_name}.{image_format.lower()}"),
        'image_format': image_format_description,
        'image_size': image_size,
        'image_resolution': image_resolution,
        'aspect_ratio': image_aspect_ratio,
        'image_mode': image_mode
    }

    update_session(request=request, user_id=user_id)

    return render(request, 'imageInfo.html', context, status=200)
