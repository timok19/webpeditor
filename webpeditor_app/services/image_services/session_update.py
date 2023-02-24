from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from django.contrib.sessions.backends.signed_cookies import SessionStore

from webpeditor import settings
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local
from webpeditor_app.services.image_services.user_folder import delete_empty_folders


def update_session(request: WSGIRequest, user_id: str) -> JsonResponse:
    """
    Update session_id token expiry to 30 minutes if it is not expired yet.
    If session_id token is expired, delete the image and the folder with the image.

    Parameters:
        request (WSGIRequest): request from view to get sessionid
        user_id (str): value of user's id to store into SessionStore
    Return:
        Response about session status and estimated time of sessionid
    """

    session_key = request.COOKIES.get('sessionid')

    try:
        session_store = SessionStore(session_key=session_key)
    except Exception as e:
        delete_empty_folders(settings.MEDIA_ROOT)
        return JsonResponse({'success': False, 'error': f'Something went wrong {e}'}, status=400)

    delete_old_image_in_db_and_local(user_id)

    current_session_expiry = round(session_store.get_expiry_age() / 60)

    session_store.encode(session_dict={'user_id': user_id})

    updated_expiration = timezone.now() + timezone.timedelta(seconds=1800)
    session_store.set_expiry(value=updated_expiration)

    session_store.save()

    total_time_expiration: int = round((session_store.get_expiry_date() - timezone.now()).seconds / 60)

    print(f"\nCurrent session expiration time: {current_session_expiry} minute(s)")
    print(f"\nSession will expire in {total_time_expiration} minute(s)\n")

    return JsonResponse({
                            'success': True, 'info': 'Session is alive',
                            'current_session_expiry_in_minutes': current_session_expiry,
                            'estimated_time_of_session_id': total_time_expiration
                        },
                        status=200)
