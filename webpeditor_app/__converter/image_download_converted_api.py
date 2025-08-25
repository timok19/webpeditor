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


@csrf_exempt
@require_http_methods(["GET"])
def download_all_converted_api(request: WSGIRequest) -> JsonResponse | None:
    converted_images: list = []
    converted_images_name_and_urls: list[str] = []

    if request.method == "GET":
        response: JsonResponse | tuple[str, list] = __get_user_id_and_converted_images(request)
        if isinstance(response, JsonResponse):
            return response

        if isinstance(response, tuple):
            converted_images = response[1]

        for image in converted_images:
            public_id: str = image[2]
            converted_images_name_and_urls.append(public_id)

        zip_url: str = download_zip_url(**{"public_ids": converted_images_name_and_urls, "resource_type": "image"})

        return JsonResponse({"zip_url": zip_url}, status=201)


def __get_user_id_and_converted_images(request: WSGIRequest) -> JsonResponse | tuple[str, list[Any]]:
    user_id: str | None = get_unsigned_user_id(request)

    if user_id is None:
        return ResultJsonResponse(result=Result.ERROR, message="User Id was not found", status_code=401)

    converted_images: list[Any] | None = request.session.get("converted_image")

    if converted_images is None:
        return ResultJsonResponse(result=Result.ERROR, message="Converted images not found", status_code=404)

    return user_id, converted_images
