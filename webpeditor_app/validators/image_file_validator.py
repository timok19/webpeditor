from typing import IO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.core.handlers.wsgi import WSGIRequest

from webpeditor.settings import MAX_IMAGE_FILE_SIZE, MAX_SUM_SIZE_OF_IMAGE_FILES, ONE_MEGABYTE, VALID_IMAGE_FORMATS_FOR_IMAGE_EDITOR


def validate_images(request: WSGIRequest, image_files: list[UploadedFile]) -> bool:
    total_size: int = 0

    for image_file in image_files:
        if isinstance(image_file, InMemoryUploadedFile):
            image_io_file: IO | None = image_file.file

            if image_io_file is None:
                request.session.pop("error_message", None)
                request.session["error_message"] = "Invalid file format. Please upload a valid image file."
                return False

            image_file_size: int | None = image_file.size

            if image_file_size is None:
                request.session.pop("error_message", None)
                request.session["error_message"] = "Failed to read the image file."
                return False

            total_size += image_file_size

            with Image.open(image_io_file) as image:
                if image.format not in VALID_IMAGE_FORMATS_FOR_IMAGE_EDITOR:
                    request.session.pop("error_message", None)
                    request.session["error_message"] = f"Invalid file format. {str(VALID_IMAGE_FORMATS_FOR_IMAGE_EDITOR)} files are allowed."
                    return False

            if image_file_size > MAX_IMAGE_FILE_SIZE:
                request.session.pop("error_message", None)
                request.session["error_message"] = f"Image size should not exceed {MAX_IMAGE_FILE_SIZE / ONE_MEGABYTE} MB."
                return False

            if total_size > MAX_SUM_SIZE_OF_IMAGE_FILES:
                request.session.pop("error_message", None)
                request.session["error_message"] = f"The total size of the images should not exceed {MAX_SUM_SIZE_OF_IMAGE_FILES / ONE_MEGABYTE} MB."
                return False

    return True
