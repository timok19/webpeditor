from django.core.files.storage import default_storage
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 2 hours
    request.session.set_expiry(25)


def update_session(request: WSGIRequest, _id: int) -> JsonResponse:
    if timezone.now().second > request.session.get_expiry_age():
        request.session.clear_expired()
        try:
            original_image_id = OriginalImage.objects.get(image_id=_id)
        except OriginalImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})

        original_image_id.delete()
        default_storage.delete(original_image_id.original_image_url.name)

        return JsonResponse("Session has been expired and Image has been deleted")
    else:
        request.session.set_expiry(25)
        return JsonResponse("Session has is alive")
