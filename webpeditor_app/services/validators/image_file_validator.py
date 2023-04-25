from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError, TooManyFilesSent
from django.core.files.uploadedfile import InMemoryUploadedFile


def validate_image_file_type(uploaded_file: InMemoryUploadedFile):
    try:
        # Open the uploaded image using Pillow
        with Image.open(uploaded_file) as img:
            valid_image_formats = ['WEBP', 'JPEG', 'JPG', 'PNG', 'JFIF', 'ICO']
            if img.format not in valid_image_formats:
                raise ValidationError(f'Invalid file format. {str(valid_image_formats)} files are allowed.')
    except OSError:
        raise ValidationError('Invalid file type. Only image files are allowed.')


def validate_image_file_size(uploaded_file: InMemoryUploadedFile):
    try:
        # Validate that the uploaded file is an image
        validate_image_file_type(uploaded_file)
    except ValidationError as e:
        raise ValidationError(e)

    if uploaded_file.size > settings.MAX_IMAGE_FILE_SIZE:
        file_size_in_mb = settings.MAX_IMAGE_FILE_SIZE / 1_000_000
        raise ValidationError(f"Image size should not exceed {file_size_in_mb} MB.")


def validate_image_files(image_files: list):
    total_size: int = 0

    for image_file in image_files:
        validate_image_file_size(image_file)

        total_size += image_file.size
        if total_size > settings.MAX_SIZE_OF_IMAGE_FILES:
            files_size_in_mb = settings.MAX_SIZE_OF_IMAGE_FILES / 1_000_000
            raise ValidationError(
                f"The total size of the images should not exceed {files_size_in_mb} MB."
            )


def validate_number_of_image_files(image_files: list):
    if len(image_files) > settings.DATA_UPLOAD_MAX_NUMBER_FILES:
        raise TooManyFilesSent(f"The number of files exceeded {settings.DATA_UPLOAD_MAX_NUMBER_FILES}.")
