from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from django.contrib.sessions.backends.signed_cookies import SessionStore

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
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
    session_key = request.session.get('sessionid')
    try:
        session_store = SessionStore(session_key=session_key)
    except Session.DoesNotExist as e:
        delete_empty_folders(settings.MEDIA_ROOT)
        return JsonResponse({'success': False, 'error': f'Something went wrong: {e}'}, status=404)

    try:
        original_image = OriginalImage.objects.filter(user_id=user_id).first()
    except OriginalImage.DoesNotExist as e:
        return JsonResponse({'success': False, 'error': f'Something went wrong: {e}'}, status=404)

    total_time_expiration_minutes = session_store.get_expiry_date().minute

    expiry_date = timezone.localtime(session_store.get_expiry_date())
    now = timezone.localtime(timezone.now())
    if now > expiry_date:
        delete_old_image_in_db_and_local(user_id)

    session_store.encode(session_dict={'user_id': user_id})
    updated_expiration = timezone.now() + timezone.timedelta(seconds=1800)
    session_store.set_expiry(value=updated_expiration)
    session_store.save()

    original_image.session_id_expiration_date = session_store.get_expiry_date()
    original_image.save()

    print(f"\nSession will expire in {total_time_expiration_minutes} minute(s)\n")

    return JsonResponse({
                            'success': True, 'info': 'Session is alive',
                            'estimated_time_of_session_id': total_time_expiration_minutes
                        },
                        status=200)
