from django.contrib.sessions.models import Session
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils import timezone

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage

from pathlib import Path
import shutil


def set_session_expiry(request: WSGIRequest):
    # Set session_id token expiry to 2 hours
    request.session.set_expiry(7200)


def update_session(session_id: str) -> JsonResponse:
    session = Session.objects.filter(session_key=session_id).first()
    original_image = OriginalImage.objects.filter(session_id=session_id).first()

    if timezone.now() > session.expire_date:

        if original_image:
            original_image.delete()
            path_to_old_image_folder = Path(settings.MEDIA_ROOT) / session_id

            if path_to_old_image_folder.exists():
                shutil.rmtree(path_to_old_image_folder)

        if session:
            session.delete()

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
