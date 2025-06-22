from typing import Any, Union, Optional

import cloudinary.uploader  # pyright: ignore [reportMissingTypeStubs]
import cloudinary.api  # pyright: ignore [reportMissingTypeStubs]
from io import BytesIO
from PIL.Image import Image
from cloudinary import CloudinaryImage  # pyright: ignore [reportMissingTypeStubs]
from cloudinary.api_client.execute_request import Response  # pyright: ignore [reportMissingTypeStubs]

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http.response import ResponseHeaders, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.__converter.utils.api_response_presets import UnauthorizedAccessResponseRedirect, ResultJsonResponse, Result
from webpeditor_app.models import EditorEditedImageAsset
from webpeditor_app.services import get_original_image, get_edited_image
from webpeditor_app.core.__request_service import extract_image_edit_data_from_request_body
from webpeditor_app.services import get_unsigned_user_id, update_session


@csrf_exempt
@require_http_methods(["POST"])
def image_save_api(request: WSGIRequest) -> UnauthorizedAccessResponseRedirect | JsonResponse | ResultJsonResponse | HttpResponse | None:
    if request.method == "POST":
        user_id: Optional[str] = get_unsigned_user_id(request)

        if user_id is None:
            return UnauthorizedAccessResponseRedirect()

        if request.session.get_expiry_age() == 0:
            return UnauthorizedAccessResponseRedirect()

        original_image = get_original_image(user_id)
        if original_image is None or original_image.user_id != user_id:
            return UnauthorizedAccessResponseRedirect()

        edited_image = get_edited_image(user_id)
        if edited_image is None:
            return UnauthorizedAccessResponseRedirect()

        request_body: Union[JsonResponse, tuple[Optional[str], str, str, Optional[Image]]] = extract_image_edit_data_from_request_body(
            request
        )
        if isinstance(request_body, JsonResponse):
            return request_body

        image_file: Optional[Image] = request_body[3]

        if image_file is None:
            return ResultJsonResponse(result=Result.ERROR, message="Image file is missing", status_code=400)

        buffer: BytesIO = BytesIO()
        image_file.save(buffer, format=image_file.format)
        buffer.seek(0)

        resources: Response = cloudinary.api.resources(prefix=f"{user_id}/edited", type="upload")
        public_ids: list[Any] = [resource["public_id"] for resource in resources["resources"]]

        # Save image to Cloudinary
        cloudinary_parameters: dict[str, Union[bool, Any]] = {"public_id": public_ids[0], "overwrite": True}
        cloudinary_image: CloudinaryImage = cloudinary.uploader.upload_image(file=buffer, **cloudinary_parameters)

        update_session(request=request, user_id=user_id)

        # Update edited image in DB
        EditorEditedImageAsset.objects.filter(user_id=user_id).update(image_url=cloudinary_image.url)

        response: HttpResponse = HttpResponse()
        response.status_code = 200
        response.headers = ResponseHeaders({"Content-Type": "text/javascript"})

        return response
