import logging
import uuid

from django.contrib.sessions.backends.db import SessionStore
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_service import delete_old_image_in_db_and_local

logging.basicConfig(level=logging.INFO)


def set_session_expiry(request: WSGIRequest, num_of_seconds: int):
    request.session.set_expiry(num_of_seconds)


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


def update_session_store(session_store: SessionStore, user_id: str) -> SessionStore:
    session_store.encode(session_dict={'user_id': user_id})
    update_expiration = timezone.now() + timezone.timedelta(seconds=900)
    session_store.set_expiry(value=update_expiration)
    session_store.save()

    return session_store


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
    original_image = OriginalImage.objects.filter(user_id=user_id).first()
    if original_image is None:
        return JsonResponse({'success': False, 'error': 'Original image was not found'}, status=404)

    edited_image = EditedImage.objects.filter(user_id=user_id).first()
    if edited_image is None:
        return JsonResponse({'success': False, 'error': 'Edited image was not found'}, status=404)

    expiry_date = session_store.get_expiry_date()
    original_image.session_id_expiration_date = expiry_date
    original_image.save()

    edited_image.session_id_expiration_date = expiry_date
    edited_image.save()


def update_session(request: WSGIRequest, user_id: str) -> JsonResponse:
    session_key = get_session_id(request)

    session_store = SessionStore(session_key=session_key)
    if session_store is None:
        return JsonResponse({'success': False, 'error': f'Session store does not exist'}, status=404)

    current_time_expiration_minutes = round(session_store.get_expiry_age() / 60)

    expiry_date = timezone.localtime(session_store.get_expiry_date())
    now = timezone.localtime(timezone.now())
    if now > expiry_date:
        delete_old_image_in_db_and_local(user_id)
        session_store.clear_expired()

    session_store = update_session_store(session_store, user_id)
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
