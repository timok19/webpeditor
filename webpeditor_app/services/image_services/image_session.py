import shutil
from pathlib import Path

from django.http import JsonResponse
from django.utils import timezone

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage


def delete_expired_image_session(user_id: str):
    """
    Deletes the expired image session and the corresponding image from the user's media folder.

    Args:
        user_id (str): The ID of the user whose image and image session is being checked.

    Returns:
        A JSON response with success status and information message.
    """

    original_image = OriginalImage.objects.filter(user_id=user_id).first()
    path_to_old_image_folder = Path(settings.MEDIA_ROOT) / user_id

    if original_image and timezone.now() > original_image.session_id_expiration_date:
        original_image.delete()
        if path_to_old_image_folder.exists():
            shutil.rmtree(path_to_old_image_folder)
        return JsonResponse({'success': True, 'info': 'Session has been expired and image has been deleted'},
                            status=204)
