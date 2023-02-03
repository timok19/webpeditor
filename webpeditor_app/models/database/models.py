from django.db import models
from django.utils import timezone


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image = models.ImageField(upload_to="", max_length=6_000_000, default=None)
    session_id = models.CharField(max_length=1023, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    content_type_edited = models.CharField(max_length=255)
    edited_image_path = models.ImageField(upload_to="", max_length=6_000_000, default=None)
    session_id = models.CharField(max_length=1023, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
