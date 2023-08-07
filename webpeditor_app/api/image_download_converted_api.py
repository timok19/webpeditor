import logging

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.api.api_utils.create_zip_with_converted_images import (
    create_zip_with_converted_images,
)
from webpeditor_app.api.api_utils.response_presets import (
    get_user_id_and_converted_images,
)

logging.basicConfig(level=logging.INFO)


@csrf_exempt
@require_http_methods(["GET"])
def image_download_converted_api(request: WSGIRequest) -> JsonResponse:
    if request.method == "GET":
        converted_images: list = []

        response: JsonResponse | tuple[str, list] = get_user_id_and_converted_images(
            request
        )
        if isinstance(response, JsonResponse):
            return response

        if isinstance(response, tuple):
            converted_images = response[1]

        return JsonResponse({"converted_images": converted_images}, status=200)
    else:
        return JsonResponse({"error": "Forbidden request"}, status=405)


@csrf_exempt
@require_http_methods(["GET"])
def download_all_converted_api(request: WSGIRequest) -> JsonResponse | FileResponse:
    converted_images: list = []
    converted_images_name_and_urls: list[str] = []

    if request.method == "GET":
        response: JsonResponse | tuple[str, list] = get_user_id_and_converted_images(
            request
        )
        if isinstance(response, JsonResponse):
            return response

        if isinstance(response, tuple):
            converted_images = response[1]

        for image in converted_images:
            public_id: str = image[2]
            converted_images_name_and_urls.append(public_id)

        zip_url: str = create_zip_with_converted_images(converted_images_name_and_urls)

        return JsonResponse({"zip_url": zip_url}, status=201)
