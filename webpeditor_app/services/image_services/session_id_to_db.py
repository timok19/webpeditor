import shutil
from pathlib import Path

from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.user_folder import delete_empty_folders


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 15 minutes
    request.session.set_expiry(15 * 60)


def update_session(session_id: str, user_id: str) -> JsonResponse:
    """
    Update session_id token expiry to 2 hours if it is not expired yet.
    If session_id token is expired, delete the image and the folder with the image.

    Parameters:
        session_id: session_id token
        user_id: user_folder_name token
    Return:
        JsonResponse with information about the user_folder_name token
    """
    try:
        session = Session.objects.get(session_key=session_id)
    except Session.DoesNotExist:
        delete_empty_folders(settings.MEDIA_ROOT)
        return JsonResponse({'success': False, 'error': 'Invalid session_id'}, status=400)

    original_image = OriginalImage.objects.filter(user_id=user_id).first()
    path_to_old_image_folder = Path(settings.MEDIA_ROOT) / user_id

    if original_image and timezone.now() > original_image.session_id_expiration_date:
        original_image.delete()
        if path_to_old_image_folder.exists():
            shutil.rmtree(path_to_old_image_folder)
        return JsonResponse({'success': True, 'info': 'Session has been expired and image has been deleted'},
                            status=204)

    session.expire_date = timezone.now() + timezone.timedelta(seconds=7200)
    session.save()
    print(f"\nSession will expire at {session.expire_date}")
    return JsonResponse(
        {'success': True, 'info': 'Session is alive', 'estimated_time_of_session_id': str(session.expire_date)},
        status=200)
