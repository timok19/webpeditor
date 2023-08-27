from io import BytesIO
import imghdr
from types import NoneType

from django.core.handlers.asgi import ASGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.database.models.original_image_model import OriginalImage
from webpeditor_app.commands.original_images_commands import OriginalImagesCommands

from webpeditor_app.services.image_services.image_editor_service import (
    get_data_from_image_url,
)
from webpeditor_app.services.other_services.session_service import SessionService


@csrf_exempt
@require_http_methods(["GET"])
async def image_get_original_api(request: ASGIRequest):
    session_service = SessionService(request)
    user_id = session_service.user_id

    original_images_commands = OriginalImagesCommands(user_id)

    if request.method == "GET":
        if isinstance(user_id, NoneType):
            return JsonResponse({"error": "User Id was not found"}, status=401)

        original_image: OriginalImage | None = (
            await original_images_commands.get_original_image()
        )
        if isinstance(original_image, NoneType):
            return JsonResponse({"error": "Original image was not found"}, status=404)

        image_url: str = original_image.image_url
        image_name: str = original_image.image_name

        image_data: BytesIO = get_data_from_image_url(image_url)
        image_format = imghdr.what(image_data)
        image_name_with_extension: str = f"{image_name}.{image_format}"

        response_data = {
            "image_url": image_url,
            "image_name": image_name_with_extension,
        }

        return JsonResponse(response_data, status=200)
