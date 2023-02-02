from django.db import models
from datetime import datetime


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image = models.BinaryField()
    session_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    content_type_edited = models.CharField(max_length=255)
    edited_image = models.BinaryField()
    session_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
