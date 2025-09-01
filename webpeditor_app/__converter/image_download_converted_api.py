from typing import Any

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def image_download_converted_api(request: WSGIRequest) -> JsonResponse:
    if request.method == "GET":
        converted_images: list[Any] = []

        response: JsonResponse | tuple[str, list[Any]] = __get_user_id_and_converted_images(request)
        if isinstance(response, JsonResponse):
            return response

        if isinstance(response, tuple):
            converted_images = response[1]

        return ResultJsonResponse(result=Result.SUCCESS, data={"converted_images": converted_images}, status_code=200)
    else:
        return ResultJsonResponse(result=Result.ERROR, message="Forbidden request", status_code=405)
