from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_in_db_and_local import delete_old_image_in_db_and_local
from webpeditor_app.services.image_services.user_folder import delete_empty_folders


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 15 minutes
    request.session.set_expiry(900)


def get_session_id(request: WSGIRequest) -> str | None:
    try:
        session_id = request.session.session_key
        if session_id:
            return session_id
    except TypeError as e:
        print(e)
        return None


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

    session_key = get_session_id(request)
    current_time_expiration_minutes = 0

    try:
        session_store = SessionStore(session_key=session_key)
    except Session.DoesNotExist as e:
        delete_empty_folders(settings.MEDIA_ROOT)
        return JsonResponse({'success': False, 'error': f'Something went wrong: {e}'}, status=404)

    try:
        original_image = OriginalImage.objects.filter(user_id=user_id).first()
    except OriginalImage.DoesNotExist as e:
        return JsonResponse({'success': False, 'error': f'Something went wrong: {e}'}, status=404)

    try:
        edited_image = EditedImage.objects.filter(user_id=user_id).first()
    except EditedImage.DoesNotExist as e:
        return JsonResponse({'success': False, 'error': f'Something went wrong: {e}'}, status=404)

    if session_store:
        # Set cookie expiration time to 15 minutes
        current_time_expiration_minutes = round(session_store.get_expiry_age() / 60)
        print(
            f"\nCurrent session expiration time of user \'{original_image.user_id or edited_image.user_id}\': "
            f"{current_time_expiration_minutes} minute(s)"
        )

        expiry_date = timezone.localtime(session_store.get_expiry_date())
        now = timezone.localtime(timezone.now())
        if now > expiry_date:
            delete_old_image_in_db_and_local(user_id)
            session_store.clear_expired()

        session_store.encode(session_dict={'user_id': user_id})
        update_expiration = timezone.now() + timezone.timedelta(seconds=900)

        session_store.set_expiry(value=update_expiration)
        session_store.save()

        new_time_expiration_minutes = round(session_store.get_expiry_age() / 60)
        print(
            f"Updated session expiration time of user \'{original_image.user_id or edited_image.user_id}\': "
            f"{new_time_expiration_minutes} minute(s)\n"
        )

    if original_image:
        original_image.session_id_expiration_date = session_store.get_expiry_date()
        original_image.save()

    if edited_image:
        edited_image.session_id_expiration_date = session_store.get_expiry_date()
        edited_image.save()

    return JsonResponse({
        'success': True, 'info': 'Session is alive',
        'estimated_time_of_session_id': current_time_expiration_minutes
    },
        status=200)
