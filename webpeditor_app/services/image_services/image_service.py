import io
import logging
import os
import shutil
from pathlib import Path

from PIL import Image as PilImage
from PIL.Image import Image as ImageClass
from _decimal import ROUND_UP, Decimal
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse
from rest_framework.utils.serializer_helpers import ReturnDict

from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer, EditedImageSerializer
from webpeditor_app.services.image_services.folder_service import create_folder, get_media_root_paths, \
    delete_users_folder

logging.basicConfig(level=logging.INFO)


def delete_old_image_in_db_and_local(user_id: str) -> JsonResponse:
    """
    Deletes the expired image session and the corresponding image from the user's media folder.

    Args:
        user_id (str): The ID of the user whose image and image session is being checked.

    Returns:
        A JSON response with success status and information message.
    """
    path_to_old_user_folder = Path(settings.MEDIA_ROOT) / user_id

    original_image = get_original_image(user_id)
    if original_image:
        session_store = SessionStore(session_key=original_image.session_id)
        session_store.delete()
        original_image.delete()
        logging.info("Original image has been deleted from db.\nClearing session...")

    edited_image = get_edited_image(user_id)
    if edited_image:
        edited_image.delete()
        logging.info("Edited image has been deleted from db.")

    # Delete user's folder in all other cases
    if not original_image and not edited_image:
        logging.info("No images in db. Deleting user folder...")
        delete_users_folder(path_to_old_user_folder)

    return JsonResponse({
        'success': True,
        'info': 'Session has been expired and image has been deleted'
    }, status=204)


def get_serialized_data_original_image() -> ReturnDict:
    original_images = get_all_original_images()
    original_image_serializer = OriginalImageSerializer(original_images, many=True)

    return original_image_serializer.data


def get_serialized_data_edited_image() -> ReturnDict:
    edited_images = get_all_edited_images()
    edited_image_serializer = EditedImageSerializer(edited_images, many=True)

    return edited_image_serializer.data


def get_all_original_images():
    original_images = OriginalImage.objects.all()
    if original_images is None:
        raise ValueError("Original images do not exist in db")

    return original_images


def get_all_edited_images():
    edited_images = EditedImage.objects.all()
    if edited_images is None:
        raise ValueError("Edited images do not exist in db")

    return edited_images


def get_original_image(user_id: str) -> OriginalImage | None:
    original_image = OriginalImage.objects.filter(user_id=user_id).first()
    if original_image is None:
        return None

    return original_image


def get_edited_image(user_id: str) -> EditedImage | None:
    edited_image = EditedImage.objects.filter(user_id=user_id).first()
    if edited_image is None:
        return None

    return edited_image


def get_image_file_instance(path_to_local_image: Path | str) -> ImageClass | None:
    try:
        return PilImage.open(path_to_local_image)
    except (FileExistsError, FileNotFoundError):
        return None


def format_image_file_name(image_name: str) -> str:
    basename, ext = os.path.splitext(image_name)
    if len(basename) > 20:
        basename = basename[:17] + "..."
    return basename + ext


def get_extension_in_upper_case(image_name: str) -> str:
    return os.path.splitext(image_name)[1][1:].upper()


def get_image_file_size(image: ImageClass) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=image.format)

    size_in_bytes: int = buffer.tell()
    size_in_kb: float = size_in_bytes / 1024

    if size_in_kb >= 1024:
        # Calculate the size in megabytes
        size_in_mb: float = size_in_kb / 1024
        return f"{size_in_mb:.1f} MB"
    else:
        return f"{size_in_kb:.1f} KB"


def get_image_aspect_ratio(image_file: ImageClass):
    return Decimal(image_file.width / image_file.height).quantize(Decimal('.1'), rounding=ROUND_UP)


def get_original_image_file_path(user_id: str, original_image) -> Path:
    # Get first argument from get_media_root_paths() to get original image path
    return get_media_root_paths(user_id)[0] / original_image.image_name


def get_edited_image_file_path(user_id: str, edited_image: EditedImage) -> Path:
    # Get second argument from get_media_root_paths() to get edited image path
    return get_media_root_paths(user_id)[1] / edited_image.edited_image_name


def copy_original_image_to_edited_folder(user_id: str,
                                         original_image: OriginalImage,
                                         edited_image: EditedImage) -> bool:
    original_image_folder_path, edited_image_folder_path = get_media_root_paths(user_id)

    if not edited_image_folder_path.exists():
        create_folder(user_id=user_id, is_original_image=False)

    original_image_file_path = get_original_image_file_path(user_id, original_image)
    edited_image_file_path = get_edited_image_file_path(user_id, edited_image)

    shutil.copy2(original_image_file_path, edited_image_file_path)

    if get_image_file_instance(edited_image_file_path) is None:
        return False

    return True
