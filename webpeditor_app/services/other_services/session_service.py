import logging
import uuid

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.folder_service import delete_empty_folders
from webpeditor_app.services.image_services.image_service import delete_old_image_in_db_and_local

logging.basicConfig(level=logging.INFO)


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 15 minutes
    request.session.set_expiry(900)


def get_session_id(request: WSGIRequest) -> str | None:
    try:
        session_id = request.session.session_key
        if session_id:
            return session_id
    except TypeError as e:
        logging.error(e)
        return None


def create_user_id() -> str:
    return str(uuid.uuid4())


def get_or_add_user_id(request: WSGIRequest) -> str:
    if "user_id" not in request.session:
        request.session["user_id"] = create_user_id()
    return request.session["user_id"]


def get_user_id_from_session_store(request: WSGIRequest) -> str | None:
    try:
        return request.session.get("user_id")
    except Exception as e:
        logging.error(e)
        return None


def update_image_editor_session(request: WSGIRequest, user_id: str) -> JsonResponse:
    """
    Update session_id token expiry to 30 minutes if it is not expired yet.
    If session_id token is expired, delete the image and the folder with the image.

    Parameters:
        request (WSGIRequest): request from view to get sessionid
        user_id (str): value of user's id to store into SessionStore
    Return:
        Response about session status and estimated time of sessionid
    """

    session_store, \
        current_time_expiration_minutes, \
        new_time_expiration_minutes, \
        _ = update_session(request=request, user_id=user_id)

    original_image: OriginalImage = OriginalImage.objects.filter(user_id=user_id).first()
    if original_image is None:
        return JsonResponse({'success': False, 'error': 'Original image was not found'}, status=404)

    edited_image: EditedImage = EditedImage.objects.filter(user_id=user_id).first()
    if edited_image is None:
        return JsonResponse({'success': False, 'error': 'Edited image was not found'}, status=404)

    if original_image:
        original_image.session_id_expiration_date = session_store.get_expiry_date()
        original_image.save()

    if edited_image:
        edited_image.session_id_expiration_date = session_store.get_expiry_date()
        edited_image.save()

    logging.info(
        f"Current session expiration time of user \'{original_image.user_id or edited_image.user_id}\': "
        f"{current_time_expiration_minutes} minute(s)"
    )

    logging.info(
        f"Updated session expiration time of user \'{original_image.user_id or edited_image.user_id}\': "
        f"{new_time_expiration_minutes} minute(s)"
    )


def update_session(request: WSGIRequest, user_id: str) \
        -> JsonResponse | tuple[SessionStore, int, int, JsonResponse]:

    session_key = get_session_id(request)
    current_time_expiration_minutes = 0
    new_time_expiration_minutes = 0

    session_store = SessionStore(session_key=session_key)
    if session_store is None:
        delete_empty_folders(settings.MEDIA_ROOT)
        return JsonResponse({'success': False, 'error': f'Session store does not exist'}, status=404)

    if session_store:
        # Set cookie expiration time to 15 minutes
        current_time_expiration_minutes = round(session_store.get_expiry_age() / 60)

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

        logging.info(
            f"Current session expiration time of anonymous user: "
            f"{current_time_expiration_minutes} minute(s)"
        )

        logging.info(
            f"Updated session expiration time of anonymous user: "
            f"{new_time_expiration_minutes} minute(s)"
        )

    return session_store, \
        current_time_expiration_minutes, \
        new_time_expiration_minutes, \
        JsonResponse({
            'success': True, 'info': 'Session is alive',
            'estimated_time_of_session_id': current_time_expiration_minutes
        }, status=200)
