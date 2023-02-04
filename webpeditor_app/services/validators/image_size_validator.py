from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_file_size(uploaded_file: UploadedFile):
    file_size = uploaded_file.size

    if file_size > settings.MAX_IMAGE_FILE_SIZE:
        raise ValidationError("File size should not exceed 6 MB.")
