import logging
import uuid

from django.contrib.sessions.backends.db import SessionStore
from django.core.handlers.wsgi import WSGIRequest
from django.core import signing
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.api_services.cloudinary_service import delete_user_folder_with_content
from webpeditor_app.services.image_services.image_service import delete_original_image_in_db

logging.basicConfig(level=logging.INFO)


def set_session_expiry(request: WSGIRequest, num_of_seconds: int):
    request.session.set_expiry(num_of_seconds)


def get_session_key(request: WSGIRequest) -> str | None:
    try:
        return request.session.session_key
    except Exception as e:
        logging.error(e)
        return None


def create_signed_user_id() -> str:
    user_id = str(uuid.uuid4())
    return signing.dumps(user_id)


def add_signed_user_id_to_session_store(request: WSGIRequest):
    request.session["user_id"] = create_signed_user_id()


def get_unsigned_user_id(request: WSGIRequest) -> str | None:
    try:
        return signing.loads(request.session["user_id"])
    except Exception as e:
        logging.error(e)
        return None


def update_session_store(session_store: SessionStore, request: WSGIRequest) -> SessionStore:
    session_store.encode(session_dict={'user_id': request.session["user_id"]})
    update_expiration = timezone.now() + timezone.timedelta(seconds=900)
    session_store.set_expiry(value=update_expiration)

    return session_store


def clear_expired_session_store(session_key: str):
    session_store = SessionStore(session_key=session_key)
    session_store.clear_expired()
    logging.info("Session has been cleared")


def log_session_expiration_times(user_id: str,
                                 current_time_expiration_minutes: int,
                                 new_time_expiration_minutes: int):
    logging.info(
        f"Current session expiration time of user \'{user_id}\': "
        f"{current_time_expiration_minutes} minute(s)"
    )

    logging.info(
        f"Updated session expiration time of user \'{user_id}\': "
        f"{new_time_expiration_minutes} minute(s)"
    )


def update_image_expiration_dates(user_id: str, session_store: SessionStore):
    original_image = OriginalImage.objects.filter(user_id=user_id)
    if original_image is None:
        return JsonResponse({'success': False, 'error': 'Original image was not found'}, status=404)

    edited_image = EditedImage.objects.filter(user_id=user_id)
    if edited_image is None:
        return JsonResponse({'success': False, 'error': 'Edited image was not found'}, status=404)

    expiry_date = session_store.get_expiry_date()
    original_image.update(session_key_expiration_date=expiry_date)
    edited_image.update(session_key_expiration_date=expiry_date)


def update_session(request: WSGIRequest, user_id: str) -> JsonResponse:
    session_key = get_session_key(request)

    session_store = SessionStore(session_key=session_key)
    if session_store is None:
        return JsonResponse({
            'success': False,
            'error': f'Session store does not exist'
        }, status=404)

    current_time_expiration_minutes = round(session_store.get_expiry_age() / 60)

    expiry_date = timezone.localtime(session_store.get_expiry_date())
    now = timezone.localtime(timezone.now())
    if now > expiry_date:
        delete_original_image_in_db(user_id)
        delete_user_folder_with_content(user_id)
        clear_expired_session_store(session_key)

    session_store = update_session_store(session_store, request)
    new_time_expiration_minutes = round(session_store.get_expiry_age() / 60)

    log_session_expiration_times(
        user_id,
        current_time_expiration_minutes,
        new_time_expiration_minutes
    )

    update_image_expiration_dates(user_id, session_store)

    return JsonResponse({
        'success': True, 'info': 'Session is alive',
        'estimated_time_of_session_id': current_time_expiration_minutes
    }, status=200)
