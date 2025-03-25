from typing import Any
from django.db import models
from django.utils import timezone


class BaseImageAsset(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.id)


class BaseImageAssetFile(models.Model):
    # TODO: Add types
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=120, blank=True)
    filename_shorter = models.CharField(max_length=30, blank=True)
    content_type = models.CharField(max_length=20)
    format = models.CharField(max_length=10, blank=True)
    format_description = models.CharField(max_length=50, blank=True)
    size = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    aspect_ratio = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    color_mode = models.CharField(max_length=10)
    exif_data: models.JSONField[Any] = models.JSONField()

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)
