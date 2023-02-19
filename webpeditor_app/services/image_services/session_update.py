from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.utils import timezone

from webpeditor import settings
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local
from webpeditor_app.services.image_services.user_folder import delete_empty_folders


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

    delete_old_image_in_db_and_local(user_id)

    session.expire_date = timezone.now() + timezone.timedelta(seconds=1800)
    session.save()

    print(f"\nSession will expire at {session.expire_date}")
    return JsonResponse(
        {'success': True, 'info': 'Session is alive', 'estimated_time_of_session_id': str(session.expire_date)},
        status=200)
