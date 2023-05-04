import json
import logging
from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.image_services.image_service import get_converted_image, get_converted_image_set_data
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id


logging.basicConfig(level=logging.INFO)


@csrf_exempt
@require_http_methods(['GET'])
def image_download_converted_api(request: WSGIRequest):
    if request.method == 'GET':
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return JsonResponse({"error": "User Id was not found"}, status=401)

        converted_image: ConvertedImage | None = get_converted_image(user_id)
        if isinstance(converted_image, NoneType) or converted_image.image_set is None:
            return JsonResponse({"error": "Converted image was not found"}, status=404)

        get_converted_image_set_data(user_id)

        try:
            image_set_data = converted_image.image_set
            image_data = image_set_data[0]
            image_url: str = image_data.get("image_url")
            image_name: str = image_data.get("image_name")
        except IndexError as e:
            logging.error(f"Error: {e}")
            return JsonResponse({"error": f"Error: {e}"}, status=500)
        except KeyError as e:
            logging.error(f"Error, value for image_url does not exist in db. {e}")
            return JsonResponse({"image_url": f"Error, value for image_url does not exist in db. {e}"}, status=500)

        return JsonResponse({"image_url": image_url, "image_name": image_name}, status=200)
    else:
        return JsonResponse({"error": "Forbidden request"}, status=405)
