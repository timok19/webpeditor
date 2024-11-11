from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from webpeditor.settings import ONE_MEGABYTE


class ConvertedImageValidator:
    @classmethod
    def validate_file_size(cls, file: UploadedFile | None) -> None:
        if not file:
            raise ValidationError("File is required")

        max_file_size: int = IMAGE_CONVERTER_SETTINGS["max_file_size"]

        if file.size and file.size > max_file_size:
            raise ValidationError("File size exceeds %s MB" % round(max_file_size / ONE_MEGABYTE))
