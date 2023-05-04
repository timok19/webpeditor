from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.image_services.image_service import get_converted_image
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id


@csrf_exempt
@require_http_methods(['POST'])
def image_get_original_api(request: WSGIRequest):
    if request.method == 'POST':
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return JsonResponse({"error": "User Id was not found"}, status=401)

        converted_image: ConvertedImage | None = get_converted_image(user_id)
        if isinstance(converted_image, NoneType):
            return JsonResponse({"error": "Converted image was not found"}, status=404)

        image_url: str = converted_image.image_set

        return JsonResponse({"image_url": image_url}, status=200)

