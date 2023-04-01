from django.db import models
from django.utils import timezone

from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    original_image = models.ImageField(upload_to="",
                                       validators=[validate_image_file_size],
                                       null=True,
                                       blank=True)
    user_id = models.CharField(max_length=32, null=True)
    session_id = models.CharField(max_length=120, null=True)
    session_id_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Original Image'
        verbose_name_plural = 'Original Images'

    def __str__(self):
        return str(self.image_id)


class EditedImage(models.Model):
    edited_image_id = models.AutoField(primary_key=True)
    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    edited_image_name = models.CharField(max_length=255, default="")
    content_type_edited = models.CharField(max_length=255)
    edited_image = models.ImageField(upload_to="",
                                     validators=[validate_image_file_size],
                                     null=True,
                                     blank=True)
    user_id = models.CharField(max_length=32, null=True)
    session_id = models.CharField(max_length=120, null=True)
    session_id_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Edited Image'
        verbose_name_plural = 'Edited Images'

    def __str__(self):
        return str(self.edited_image_id)
