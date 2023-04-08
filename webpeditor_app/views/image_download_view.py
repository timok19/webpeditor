import base64
import io
import json
import os

from PIL import Image
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.image_services.image_service import get_extension_in_upper_case
from webpeditor_app.services.other_services.session_service import get_or_add_user_id, update_image_editor_session


@requires_csrf_token
@require_http_methods(['POST'])
def image_download_view(request: WSGIRequest):
    if request.method == 'POST':
        user_id: str = get_or_add_user_id(request)

        data = json.loads(request.body)
        data_url: str = data.get('dataURL')
        mime_type: str = data.get('mimeType')
        file_name: str = data.get('fileName')

        image_data: bytes = base64.b64decode(data_url.split(',')[1])
        image_file = Image.open(io.BytesIO(image_data))

        file_extension: str = get_extension_in_upper_case(file_name)
        if file_extension == 'JPG':
            file_extension = 'JPEG'

        if file_extension == 'PNG':
            image_file_converted = image_file.convert('RGBA')
        else:
            image_file_converted = image_file.convert('RGB')

        buffer = io.BytesIO()
        image_file_converted.save(buffer, format=file_extension, quality=100)

        # Reset the buffer position to the beginning
        buffer.seek(0)

        response = HttpResponse(buffer, content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'

        update_image_editor_session(request=request, user_id=user_id)

        return response

    return JsonResponse({'error': 'Invalid request method'}, status=400)
