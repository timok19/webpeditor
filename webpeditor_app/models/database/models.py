from django.db import models
from django.utils import timezone

from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_file = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image_url = models.ImageField(upload_to="",
                                           validators=[validate_image_file_size],
                                           default=None,
                                           null=False,
                                           blank=False)
    session_id = models.CharField(max_length=1023, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.image_id


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image_file = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    content_type_edited = models.CharField(max_length=255)
    edited_image_url = models.ImageField(upload_to="",
                                         validators=[validate_image_file_size],
                                         default=None,
                                         null=False,
                                         blank=False)
    session_id = models.CharField(max_length=1023, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.edited_image_id
