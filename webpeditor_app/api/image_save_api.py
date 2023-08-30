from types import NoneType

import cloudinary.uploader
import cloudinary.api
from io import BytesIO
from PIL.Image import Image as ImageClass

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http.response import ResponseHeaders, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.api.api_utils.response_presets import unauthorized_access_response
from webpeditor_app.database.models.models import EditedImage
from webpeditor_app.services.image_services.image_service import (
    get_original_image,
    get_edited_image,
)
from webpeditor_app.services.external_api_services.request_service import (
    extract_image_edit_data_from_request_body,
)
from webpeditor_app.services.other_services.session_service import (
    get_unsigned_user_id,
    update_session,
)


@csrf_exempt
@require_http_methods(["POST"])
def image_save_api(request: WSGIRequest):
    if request.method == "POST":
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return unauthorized_access_response()

        if request.session.get_expiry_age() == 0:
            return unauthorized_access_response()

        original_image = get_original_image(user_id)
        if original_image is None or original_image.user_id != user_id:
            return unauthorized_access_response()

        edited_image = get_edited_image(user_id)
        if edited_image is None:
            return unauthorized_access_response()

        request_body = extract_image_edit_data_from_request_body(request)
        if isinstance(request_body, JsonResponse):
            return request_body

        image_file: ImageClass = request_body[3]

        buffer = BytesIO()
        image_file.save(buffer, format=image_file.format)
        buffer.seek(0)

        resources = cloudinary.api.resources(prefix=f"{user_id}/edited", type="upload")

        public_ids: list = [
            resource["public_id"] for resource in resources["resources"]
        ]

        # Save image to Cloudinary
        cloudinary_parameters: dict = {"public_id": public_ids[0], "overwrite": True}
        cloudinary_image = cloudinary.uploader.upload_image(
            file=buffer, **cloudinary_parameters
        )

        update_session(request=request, user_id=user_id)
        # Update edited image in DB
        EditedImage.objects.filter(user_id=user_id).update(
            image_url=cloudinary_image.url
        )

        response = HttpResponse()
        response.status_code = 200
        response.headers = ResponseHeaders({"Content-Type": "text/javascript"})

        return response
