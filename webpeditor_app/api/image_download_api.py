import os
from io import BytesIO

from PIL.Image import Image as ImageClass
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.http.response import ResponseHeaders
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.services.image_services.image_service import get_file_extension
from webpeditor_app.services.api_services.request_service import get_json_request_body
from webpeditor_app.services.other_services.session_service import update_session, get_unsigned_user_id


@csrf_exempt
@require_http_methods(['POST'])
def image_download_api(request: WSGIRequest) -> HttpResponse | JsonResponse:
    if request.method == 'POST':
        mime_type = ""
        file_name = ""
        image_file = ImageClass()

        user_id: str = get_unsigned_user_id(request)

        request_body = get_json_request_body(request)
        if isinstance(request_body, tuple):
            mime_type = request_body[1]
            file_name = request_body[2]
            image_file = request_body[3]

        file_extension: str = get_file_extension(file_name).upper()
        if file_extension in ['JPG', 'JFIF']:
            file_extension = 'JPEG'

        if file_extension in ['PNG', 'WEBP']:
            image_file_converted = image_file.convert('RGBA')
        else:
            image_file_converted = image_file.convert('RGB')

        buffer = BytesIO()
        image_file_converted.save(buffer, format=file_extension, quality=100)

        # Reset the buffer position to the beginning
        buffer.seek(0)
        update_session(request=request, user_id=user_id)

        response = HttpResponse()
        response.content = buffer
        response.headers = ResponseHeaders({
            'Content-Type': mime_type,
            'Content-Disposition': f'attachment; filename="{os.path.basename(file_name)}"'
        })

        return response

    return JsonResponse({'error': 'Invalid request method'}, status=400)
