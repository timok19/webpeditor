from io import BytesIO
import json
from typing import Any

from PIL.Image import Image

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from webpeditor_app.api_views.utils.api_response_presets import ResultJsonResponse, Result
from webpeditor_app.common.resultant import ResultantValue
from webpeditor_app.services import data_url_to_binary, get_image_file_instance


def extract_image_edit_data_from_request_body(request: WSGIRequest) -> ResultantValue[]:
    data: dict[str, Any] = json.loads(request.body)
    data_url: str | None = data.get("data_url")
    mime_type: str | None = data.get("mime_type")
    image_name: str | None = data.get("image_name")

    if data_url is None or mime_type is None or image_name is None:
        return ResultJsonResponse(result=Result.ERROR, message="Missing required data", status_code=400)

    image_data: BytesIO = data_url_to_binary(data_url)
    image_file: Image | None = get_image_file_instance(image_data)

    return data_url, mime_type, image_name, image_file


def extract_image_name_from_request_body(request: WSGIRequest) -> JsonResponse | str:
    data: dict[str, Any] = json.loads(request.body)
    public_id: str | None = data.get("public_id", None)

    if public_id is None:
        return ResultJsonResponse(result=Result.ERROR, message="Missing required data", status_code=400)

    return public_id
