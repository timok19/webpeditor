from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone

from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image = models.ImageField(upload_to='original_image/upload_image/',
                                       validators=[MaxLengthValidator(settings.MAX_IMAGE_FILE_SIZE),
                                                   validate_image_file_size])
    session_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    content_type_edited = models.CharField(max_length=255)
    edited_image = models.ImageField(upload_to='edited_image/upload_edited_image/')
    session_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
