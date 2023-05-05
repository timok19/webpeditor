import logging
from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.utils.serializer_helpers import ReturnDict

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.image_services.image_service import get_converted_image, \
    get_serialized_data_of_converted_image
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id


logging.basicConfig(level=logging.INFO)


@csrf_exempt
@require_http_methods(['GET'])
def image_download_converted_api(request: WSGIRequest) -> JsonResponse:
    image_converted_data_set_list = []

    if request.method == 'GET':
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return JsonResponse({"error": "User Id was not found"}, status=401)

        converted_image: ConvertedImage | None = get_converted_image(user_id)
        if isinstance(converted_image, NoneType) or converted_image.image_set is None:
            return JsonResponse({"error": "Converted image was not found"}, status=404)

        try:
            converted_image_serialized: ReturnDict = get_serialized_data_of_converted_image(user_id)
            image_set_list: list[dict] = converted_image_serialized.get("image_set")
            for image_set in image_set_list:
                image_url: str = image_set.get("image_url")
                image_name: str = image_set.get("image_name")
                public_id: str = image_set.get("public_id")
                image_converted_data_set_list.append((image_url, image_name, public_id))
                
        except IndexError as e:
            logging.error(f"Error: {e}")
            return JsonResponse({"error": f"Error: {e}"}, status=500)
        except KeyError as e:
            logging.error(f"Error, value for image_url does not exist in db. {e}")
            return JsonResponse({"image_url": f"Error, value for image_url does not exist in db. {e}"}, status=500)

        return JsonResponse({"image_converted_data_set_list": image_converted_data_set_list}, status=200)
    else:
        return JsonResponse({"error": "Forbidden request"}, status=405)
