import base64
import json
from io import BytesIO
from typing import Tuple

from PIL.Image import Image as ImageClass

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from webpeditor_app.services.image_services.image_service import get_image_file_instance


def get_json_request_body(request: WSGIRequest) -> JsonResponse | Tuple[str | None, str, str, ImageClass | None]:
    data = json.loads(request.body)
    data_url: str | None = data.get('data_url', None)
    mime_type: str | None = data.get('mime_type', None)
    file_name: str | None = data.get('file_name', None)

    if data_url is None or mime_type is None or file_name is None:
        return JsonResponse({'error': 'Missing required data'}, status=400)

    data_url = data_url.split(',')[1]
    image_data = base64.b64decode(data_url)
    image_file = get_image_file_instance(BytesIO(image_data))

    return data_url, mime_type, file_name, image_file
