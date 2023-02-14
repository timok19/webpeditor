import shutil
from pathlib import Path

from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 2 hours
    request.session.set_expiry(7200)


# Please refactor this function, make the code shorter and more readable (if possible) and add docstrings
def update_session(session_id: str) -> JsonResponse:
    """
    Update session_id token expiry to 2 hours if it is not expired yet.
    If session_id token is expired, delete the image and the folder with the image.

    Parameters:
        session_id: session_id token
    Return:
        JsonResponse with information about the session_id token
    """
    session: Session = Session.objects.filter(session_key=session_id).first()
    original_image: OriginalImage = OriginalImage.objects.filter(session_id=session_id).first()
    path_to_old_image_folder: Path = Path(settings.MEDIA_ROOT) / session_id

    # optimize this code
    if original_image:
        if timezone.now() > original_image.session_id_expiration_date:
            original_image.delete()
            if path_to_old_image_folder.exists():
                shutil.rmtree(path_to_old_image_folder)
            return JsonResponse({'success': True,
                                 'info': 'Session has been expired and image has been deleted'},
                                status=204)
        else:
            session.expire_date = timezone.now() + timezone.timedelta(seconds=7200)
            session.save()
            print(f"\nSession will expire at {session.expire_date}")
            return JsonResponse({'success': True,
                                 'info': 'Session is alive',
                                 'estimated_time_of_session_id': str(session.expire_date)},
                                status=200)
    else:
        if path_to_old_image_folder.exists():
            shutil.rmtree(path_to_old_image_folder)

        if not session:
            return JsonResponse({'success': False,
                                 'error': 'Invalid session_id'},
                                status=400)
        else:
            if timezone.now() < session.expire_date:
                session.expire_date = timezone.now() + timezone.timedelta(seconds=7200)
                session.save()
                print(f"\nSession will expire at {session.expire_date}")
                return JsonResponse({'success': True,
                                     'info': 'Session is alive',
                                     'estimated_time_of_session_id': str(session.expire_date)},
                                    status=200)
            else:
                session.delete()
                return JsonResponse({'success': True,
                                     'info': 'Session has been expired and image folder has been deleted'},
                                    status=204)

# def update_session(session_id: str) -> JsonResponse:
#     session = Session.objects.filter(session_key=session_id).first()
#     original_image = OriginalImage.objects.filter(session_id=session_id).first()
#     path_to_old_image_folder = Path(settings.MEDIA_ROOT) / session_id
#
#     if not session:
#         return JsonResponse({'success': False, 'error': 'Invalid session_id'}, status=400)
#
#     if path_to_old_image_folder.exists():
#         shutil.rmtree(path_to_old_image_folder)
#
#     if original_image and timezone.now() > original_image.created_at:
#         original_image.delete()
#         return JsonResponse({'success': True, 'info': 'Session has been expired and image has been deleted'},
#                             status=204)
#
#     session.expire_date = timezone.now() + timezone.timedelta(
#         seconds=7200) if timezone.now() < session.expire_date else session.delete() or JsonResponse(
#         {'success': True, 'info': 'Session has been expired and image folder has been deleted'}, status=204)
#     print(f"\nSession will expire at {session.expire_date}")
#     return JsonResponse(
#         {'success': True, 'info': 'Session is alive', 'estimated_time_of_session_id': str(session.expire_date)},
#         status=200)
