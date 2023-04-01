import shutil
import logging
from pathlib import Path

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse
from rest_framework.utils.serializer_helpers import ReturnDict

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer, EditedImageSerializer


def delete_old_image_in_db_and_local(user_id: str) -> JsonResponse:
    """
    Deletes the expired image session and the corresponding image from the user's media folder.

    Args:
        user_id (str): The ID of the user whose image and image session is being checked.

    Returns:
        A JSON response with success status and information message.
    """
    path_to_old_user_folder = Path(settings.MEDIA_ROOT) / user_id

    try:
        original_image = OriginalImage.objects.filter(user_id=user_id).first()
    except OriginalImage.DoesNotExist as error:
        logging.info("No original image in db. Deleting user folder...")
        if path_to_old_user_folder.exists():
            shutil.rmtree(path_to_old_user_folder)
        raise error

    try:
        edited_image = EditedImage.objects.filter(user_id=user_id).all()
    except EditedImage.DoesNotExist as error:
        if path_to_old_user_folder.exists():
            shutil.rmtree(path_to_old_user_folder)
        logging.info("No edited image in db. Deleting user folder...")
        raise error

    if original_image:
        session_store = SessionStore(session_key=original_image.session_id)
        session_store.clear_expired()
        original_image.delete()
        logging.info("Original image has been deleted from db.\nClearing session...")

    if edited_image:
        edited_image.delete()
        logging.info("Edited image has been deleted from db.")

    if path_to_old_user_folder.exists():
        shutil.rmtree(path_to_old_user_folder)

    return JsonResponse({
        'success': True,
        'info': 'Session has been expired and image has been deleted'
    },
        status=204)


def get_serialized_data_original_image() -> ReturnDict:
    try:
        original_images = OriginalImage.objects.all()
    except OriginalImage.DoesNotExist as error:
        raise error

    original_image_serializer = OriginalImageSerializer(original_images, many=True)

    return original_image_serializer.data


def get_serialized_data_edited_image() -> ReturnDict:
    try:
        edited_images = EditedImage.objects.all()
    except OriginalImage.DoesNotExist as error:
        raise error

    edited_image_serializer = EditedImageSerializer(edited_images, many=True)

    return edited_image_serializer.data
