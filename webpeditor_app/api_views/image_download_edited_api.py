import os
from io import BytesIO
from types import NoneType

from PIL.Image import Image
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.http.response import ResponseHeaders
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.api_views.utils.api_response_presets import UnauthorizedAccessResponseRedirect
from webpeditor_app.services import get_image_file_extension
from webpeditor_app.core.request_service import extract_image_edit_data_from_request_body
from webpeditor_app.services import update_session, get_unsigned_user_id


@csrf_exempt
@require_http_methods(["POST"])
def image_download_edited_api(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        mime_type: str = ""
        image_name: str = ""
        image_file: Image = Image()

        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return UnauthorizedAccessResponseRedirect()

        if request.session.get_expiry_age() == 0:
            return UnauthorizedAccessResponseRedirect()

        request_body: JsonResponse | tuple[str | None, str, str, Image | None] = extract_image_edit_data_from_request_body(request)
        if isinstance(request_body, tuple):
            mime_type = request_body[1]
            image_name = request_body[2]
            if request_body[3] is not None:
                image_file = request_body[3]

        file_extension: str = get_image_file_extension(image_name).upper()
        if file_extension in ["JPG", "JFIF"]:
            file_extension = "JPEG"

        if file_extension in ["PNG", "WEBP"]:
            image_file_converted: Image = image_file.convert("RGBA")
        else:
            image_file_converted = image_file.convert("RGB")

        buffer: BytesIO = BytesIO()
        image_file_converted.save(buffer, format=file_extension, quality=100)

        # Reset the buffer position to the beginning
        buffer.seek(0)
        update_session(request=request, user_id=user_id)

        response: HttpResponse = HttpResponse()
        response.content = buffer
        response.headers = ResponseHeaders(
            {
                "Content-Type": mime_type,
                "Content-Disposition": f'attachment; filename="{os.path.basename(image_name)}"',
            }
        )

        return response
    else:
        return HttpResponse(content="Forbidden request", status=405)
