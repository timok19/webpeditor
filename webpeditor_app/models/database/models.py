from django.db import models
from django.utils import timezone


class OriginalImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    image_url = models.CharField(max_length=350, default="")
    user_id = models.CharField(max_length=32, null=True)
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Original Image'
        verbose_name_plural = 'Original Images'

    def __str__(self):
        return str(self.image_id)


class EditedImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=255, default="")
    content_type = models.CharField(max_length=255)
    image_url = models.CharField(max_length=350, default="")
    user_id = models.CharField(max_length=32, null=True)
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Edited Image'
        verbose_name_plural = 'Edited Images'

    def __str__(self):
        return str(self.image_id)


class ConvertedImage(models.Model):
    user_id = models.CharField(max_length=32, null=True)
    image_set = models.JSONField()
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Converted Image'
        verbose_name_plural = 'Converted Images'

    def __str__(self):
        return str(self.image_set)
