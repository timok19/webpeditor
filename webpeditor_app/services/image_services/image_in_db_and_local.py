import shutil
from pathlib import Path

from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse

from webpeditor import settings

from rest_framework.utils.serializer_helpers import ReturnDict

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer


def delete_old_image_in_db_and_local(user_id: str) -> JsonResponse:
    """
    Deletes the expired image session and the corresponding image from the user's media folder.

    Args:
        user_id (str): The ID of the user whose image and image session is being checked.

    Returns:
        A JSON response with success status and information message.
    """

    original_image = OriginalImage.objects.filter(user_id=user_id).first()
    session_store = SessionStore(session_key=original_image.session_id)
    edited_image = EditedImage.objects.filter(user_id=user_id).first()

    path_to_old_user_folder = Path(settings.MEDIA_ROOT) / user_id

    if path_to_old_user_folder.exists():
        shutil.rmtree(path_to_old_user_folder)

    if original_image:
        original_image.delete()
    if edited_image:
        edited_image.delete()
    if session_store:
        session_store.delete()

    return JsonResponse({
        'success': True,
        'info': 'Session has been expired and image has been deleted'
    },
        status=204)


def get_deserialized_data_from_db() -> ReturnDict:
    try:
        original_images = OriginalImage.objects.all()
    except OriginalImage.DoesNotExist as error:
        raise error

    original_image_serializer = OriginalImageSerializer(original_images, many=True)

    return original_image_serializer.data
