from django.contrib.sessions.models import Session
from django.core.files.storage import default_storage
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 2 hours
    request.session.set_expiry(7200)


def update_session(session_id: str) -> JsonResponse:
    try:
        session = Session.objects.filter(session_key=session_id).first()
    except Session.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)

    if not session.session_key or not session.expire_date:
        return JsonResponse({'success': False, 'error': 'Session key or session expire date not found'}, status=404)

    if timezone.now() > session.expire_date:
        try:
            original_image = OriginalImage.objects.filter(session_id=session_id).first()
        except OriginalImage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        original_image.delete()
        default_storage.delete(original_image.original_image_url.name)
        session.delete()

        return JsonResponse({'success': True,
                             'info': 'Session has been expired and image has been deleted'},
                            status=204)

    else:
        session.expire_date = timezone.now() + timezone.timedelta(seconds=7200)
        session.save()
        return JsonResponse({'success': True, 'info': 'Session is alive'}, status=200)
