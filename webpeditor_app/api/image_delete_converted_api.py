from types import NoneType

from django.core.handlers.asgi import ASGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.database.models.converted_image_model import ConvertedImage
from webpeditor_app.commands.converted_images_commands import ConvertedImagesCommands

from webpeditor_app.services.other_services.cloudinary_service import (
    CloudinaryService,
)
from webpeditor_app.services.other_services.request_service import (
    extract_image_name_from_request_body,
)
from webpeditor_app.services.other_services.session_service import SessionService


@csrf_exempt
@require_http_methods(["POST"])
async def image_delete_converted_api(request: ASGIRequest) -> JsonResponse:
    session_service = SessionService(request)
    user_id = session_service.user_id

    if request.method == "POST":
        if isinstance(user_id, NoneType):
            return JsonResponse({"error": "User Id was not found"}, status=401)

        request_body: JsonResponse | str = extract_image_name_from_request_body(request)
        if isinstance(request_body, JsonResponse):
            return request_body

        converted_image: ConvertedImage | None = (
            await ConvertedImagesCommands.get_converted_image(user_id)
        )
        if isinstance(converted_image, NoneType):
            return JsonResponse(
                {"error": "Converted image was not found in db"}, status=404
            )

        public_id: str = request_body

        image_set_list: list = converted_image.image_set
        # Delete image in cloudinary
        CloudinaryService.delete_all_assets_in_subfolder(user_id, public_id)

        filtered_image_set_list = [
            image_set
            for image_set in image_set_list
            if image_set["public_id"] != public_id
        ]
        converted_image.image_set = filtered_image_set_list
        await converted_image.save()

        converted_images: list[tuple] = request.session.get("converted_images")
        if isinstance(converted_images, NoneType):
            return JsonResponse({"error": "Converted images not found"}, status=404)

        request.session["converted_images"] = [
            image for image in converted_images if public_id not in image
        ]

        await session_service.update_session()

        return JsonResponse(
            {"success": True, "message": "Image has been deleted successfully"},
            status=200,
        )
    else:
        return JsonResponse({"error": "Forbidden request"}, status=405)
