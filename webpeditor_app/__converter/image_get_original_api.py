from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def image_get_original_api(request: WSGIRequest):
    ...
    # if request.method == "GET":
    #     user_id: str | None = get_unsigned_user_id(request)
    #
    #     original_image: EditorOriginalImageAsset | None = get_original_image(user_id)
    #
    #     image_url: str = original_image.image_url
    #     image_name: str = original_image.image_name
    #
    #     image_data: BytesIO | None = get_data_from_image_url(image_url)
    #
    #     image_format: str | None = imghdr.what(image_data)
    #     image_name_with_extension: str = f"{image_name}.{image_format}"
    #
    #     response_data: dict[str, str] = {"image_url": image_url, "image_name": image_name_with_extension}
    #
    #     return JsonResponse(response_data, status=200)
