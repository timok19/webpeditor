from io import BytesIO
import imghdr

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.image_services.image_service import get_data_from_image_url, get_original_image
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id


@csrf_exempt
@require_http_methods(['GET'])
def image_get_original_api(request: WSGIRequest):
    user_id = get_unsigned_user_id(request)

    if request.method == 'GET':

        original_image = get_original_image(user_id)
        if original_image is None:
            return JsonResponse({"error": "Original image was not found"})

        image_url: str = original_image.image_url
        image_name: str = original_image.image_name

        image_data: BytesIO = get_data_from_image_url(image_url)
        image_format = imghdr.what(image_data)
        image_name_with_extension: str = f"{image_name}.{image_format}"

        response_data = {
            "image_url": image_url,
            "image_name": image_name_with_extension
        }

        return JsonResponse(response_data)
