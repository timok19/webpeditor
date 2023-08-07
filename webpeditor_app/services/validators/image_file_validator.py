from typing import List

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest

from webpeditor.settings import (
    MAX_IMAGE_FILE_SIZE,
    MAX_SUM_SIZE_OF_IMAGE_FILES,
    ONE_MEGABYTE,
    VALID_IMAGE_FORMATS,
)


def validate_images(
    request: WSGIRequest, image_files: List[InMemoryUploadedFile]
) -> bool:
    total_size = 0

    for image_file in image_files:
        total_size += image_file.size

        if isinstance(image_file, InMemoryUploadedFile):
            image = Image.open(image_file)
            if image.format not in VALID_IMAGE_FORMATS:
                request.session.pop("error_message", None)
                request.session[
                    "error_message"
                ] = f"Invalid file format. {str(VALID_IMAGE_FORMATS)} files are allowed."
                return False

            if image_file.size > MAX_IMAGE_FILE_SIZE:
                request.session.pop("error_message", None)
                request.session[
                    "error_message"
                ] = f"Image size should not exceed {MAX_IMAGE_FILE_SIZE / ONE_MEGABYTE} MB."
                return False

            if total_size > MAX_SUM_SIZE_OF_IMAGE_FILES:
                request.session.pop("error_message", None)
                request.session["error_message"] = (
                    f"The total size of the images should not exceed "
                    f"{MAX_SUM_SIZE_OF_IMAGE_FILES / ONE_MEGABYTE} MB."
                )
                return False

    return True
