from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_file_type(uploaded_file: UploadedFile):
    try:
        # Open the uploaded image using Pillow
        with Image.open(uploaded_file) as img:
            valid_image_formats = ['WEBP', 'JPEG', 'JPG', 'PNG', 'RAW', 'JFIF', 'ICO']
            if img.format not in valid_image_formats:
                raise ValidationError(f'Invalid file format. {str(valid_image_formats)} files are allowed.')
    except OSError:
        raise ValidationError('Invalid file type. Only image files are allowed.')


def validate_image_file_size(uploaded_file: UploadedFile):
    try:
        # Validate that the uploaded file is an image
        validate_image_file_type(uploaded_file)
    except ValidationError as e:
        raise ValidationError(e)

    if uploaded_file.size > settings.MAX_IMAGE_FILE_SIZE:
        raise ValidationError("Image size should not exceed 6 MB.")
