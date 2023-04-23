import os
from wsgiref.util import FileWrapper

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_service import get_original_image
from webpeditor_app.services.other_services.session_service import get_or_add_user_id


@requires_csrf_token
@require_http_methods(['GET'])
def image_get_original_api(request: WSGIRequest):
    user_id = get_or_add_user_id(request)

    if request.method == 'GET':
        try:
            original_image = get_original_image(user_id)

            image_path = original_image.original_image.path
            content_type = original_image.content_type
            image_name = original_image.image_name

            wrapper = FileWrapper(open(image_path, 'rb'))

            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(image_path)}'
            response['X-Image-Name'] = image_name
            return response

        except OriginalImage.DoesNotExist:
            return HttpResponse(status=404)
