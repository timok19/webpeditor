from io import BytesIO
import imghdr
from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.__converter.utils.api_response_presets import ResultJsonResponse, Result
from webpeditor_app.models import EditorOriginalImageAsset
from webpeditor_app.services import get_data_from_image_url, get_original_image
from webpeditor_app.services import get_unsigned_user_id


@csrf_exempt
@require_http_methods(["GET"])
def image_get_original_api(request: WSGIRequest):
    if request.method == "GET":
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return ResultJsonResponse(result=Result.ERROR, message="User Id was not found", status_code=401)

        original_image: EditorOriginalImageAsset | None = get_original_image(user_id)
        if isinstance(original_image, NoneType):
            return ResultJsonResponse(result=Result.ERROR, message="Original image was not found", status_code=404)

        image_url: str = original_image.image_url
        image_name: str = original_image.image_name

        image_data: BytesIO | None = get_data_from_image_url(image_url)

        if image_data is None:
            return ResultJsonResponse(result=Result.ERROR, message="Failed to download image", status_code=500)

        image_format: str | None = imghdr.what(image_data)
        image_name_with_extension: str = f"{image_name}.{image_format}"

        response_data: dict[str, str] = {"image_url": image_url, "image_name": image_name_with_extension}

        return JsonResponse(response_data, status=200)
