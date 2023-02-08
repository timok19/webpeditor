from django.core.files.storage import default_storage
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 2 hours
    request.session.set_expiry(7200)


def update_session(request: WSGIRequest, session_id: str) -> JsonResponse:
    if timezone.now().second > request.session.get_expiry_age():
        request.session.clear_expired()
        try:
            original_image_session_id = OriginalImage.objects.get(session_id=session_id)
        except OriginalImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        original_image_session_id.delete()
        default_storage.delete(original_image_session_id.original_image_url.name)

        return JsonResponse("Session has been expired and Image has been deleted", status=204)
    else:
        request.session.set_expiry(7200)
        return JsonResponse("Session is alive", status=200)
