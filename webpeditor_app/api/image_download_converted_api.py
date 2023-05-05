import logging
from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.other_services.session_service import get_unsigned_user_id


logging.basicConfig(level=logging.INFO)


@csrf_exempt
@require_http_methods(['GET'])
def image_download_converted_api(request: WSGIRequest) -> JsonResponse:
    if request.method == 'GET':
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return JsonResponse({"error": "User Id was not found"}, status=401)

        converted_images: list | None = request.session.get("converted_images")
        if isinstance(converted_images, NoneType):
            return JsonResponse({"error": "Converted images not found"}, status=404)

        return JsonResponse({"converted_images": converted_images}, status=200)
    else:
        return JsonResponse({"error": "Forbidden request"}, status=405)
