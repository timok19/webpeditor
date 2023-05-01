import base64
import logging
import os
import sys
from io import BytesIO
from time import sleep
from typing import Tuple

import requests
from PIL import Image as PilImage, ExifTags
from PIL.Image import Image as ImageClass
from _decimal import ROUND_UP, Decimal
from django.http import JsonResponse
from rest_framework.utils.serializer_helpers import ReturnDict

from webpeditor_app.models.database.models import OriginalImage, EditedImage, ConvertedImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer, EditedImageSerializer, \
    ConvertedImageSerializer
from webpeditor_app.services.api_services.cloudinary_service import delete_user_folder_with_content

logging.basicConfig(level=logging.INFO)


def delete_original_image_in_db(user_id: str) -> JsonResponse:
    original_image = get_original_image(user_id)
    if original_image is None:
        logging.info("No original image in db. Deleting user's folder...")
        delete_user_folder_with_content(user_id)
    else:
        original_image.delete()

    logging.info("Original image has been deleted from db")

    return JsonResponse({
        'success': True,
        'info': 'Original and Edited images have been deleted in db'
    }, status=204)


def delete_converted_image_in_db(user_id: str) -> JsonResponse:
    converted_image = get_converted_image(user_id)
    if converted_image is None:
        logging.info("No converted image in db. Deleting user's folder...")
        delete_user_folder_with_content(user_id)
    else:
        converted_image.delete()

    logging.info("Converted image has been deleted from db")

    return JsonResponse({
        'success': True,
        'info': 'Converted image has been deleted in db'
    }, status=204)


def get_serialized_data_original_image() -> ReturnDict:
    original_images = get_all_original_images()
    original_image_serializer = OriginalImageSerializer(original_images, many=True)

    return original_image_serializer.data


def get_serialized_data_edited_image() -> ReturnDict:
    edited_images = get_all_edited_images()
    edited_image_serializer = EditedImageSerializer(edited_images, many=True)

    return edited_image_serializer.data


def get_serialized_data_converted_image() -> ReturnDict:
    converted_images = get_all_converted_images()
    converted_image_serializer = ConvertedImageSerializer(converted_images, many=True)

    return converted_image_serializer.data


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


def get_all_converted_images():
    converted_images = ConvertedImage.objects.all()
    if converted_images is None:
        raise ValueError("Converted images do not exist in db")

    return converted_images


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


def get_converted_image(user_id: str) -> ConvertedImage | None:
    converted_image = ConvertedImage.objects.filter(user_id=user_id).first()
    if converted_image is None:
        return None

    return converted_image


def data_url_to_binary(data_url: str) -> BytesIO:
    data_url = data_url.split(',')[1]
    image_data = base64.b64decode(data_url)

    return BytesIO(image_data)


def get_image_file_instance(image_data: BytesIO) -> ImageClass | None:
    try:
        image_data.seek(0)
        return PilImage.open(image_data)
    except Exception as e:
        logging.error(e)
        return None


def image_name_shorter(image_name: str) -> str:
    basename, ext = os.path.splitext(image_name)
    if len(basename) > 20:
        basename = basename[:17] + "..."

    return basename + ext


def get_image_file_extension(image_name: str) -> str:
    return os.path.splitext(image_name)[1][1:]


def get_image_file_name(image_name: str) -> str:
    return os.path.splitext(image_name)[0]


def get_data_from_image_url(image_url: str) -> BytesIO | None:
    response = requests.get(image_url)
    sleep(0.25)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        logging.error(f"Failed to download image: {response.status_code}")
        return None


def get_image_file_size(image: ImageClass) -> str:
    buffer = BytesIO()
    image.save(buffer, format=image.format)

    size_in_bytes: int = buffer.tell()
    size_in_kb: float = size_in_bytes / 1024

    if size_in_kb >= 1024:
        # Calculate the size in megabytes
        size_in_mb: float = size_in_kb / 1024
        return f"{size_in_mb:.1f} MB"
    else:
        return f"{size_in_kb:.1f} KB"


def get_image_info(image_data: BytesIO) \
        -> None | Tuple:
    image_file = get_image_file_instance(image_data)
    if image_file is None:
        return None

    image_format_description = image_file.format_description
    image_size = get_image_file_size(image_file)
    image_resolution = f"{image_file.width}px ⨯ {image_file.height}px"
    image_aspect_ratio = get_image_aspect_ratio(image_file)
    image_mode = image_file.mode
    image_format = image_file.format
    metadata = image_file.info

    # Get structured exif data, if exists
    exif_data = image_file.getexif()
    if len(exif_data) == 0:
        exif_data = "No exif data was found"
    else:
        exif_data = {
            ExifTags.TAGS[k]: v
            for k, v in exif_data.items()
            if k in ExifTags.TAGS
        }

    image_file.close()

    return image_format_description, \
        image_format, \
        image_size, \
        image_resolution, \
        image_aspect_ratio, \
        image_mode, \
        exif_data, \
        metadata


def get_image_aspect_ratio(image_file: ImageClass) -> Decimal:
    return Decimal(image_file.width / image_file.height).quantize(Decimal('.1'), rounding=ROUND_UP)
