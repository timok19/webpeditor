from datetime import datetime
from decimal import Decimal
from typing import Optional
from django.db import models
from django.utils import timezone


class BaseImageAsset(models.Model):
    id: models.AutoField[int, int] = models.AutoField(primary_key=True)
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract: bool = True
        ordering: list[str] = ["-created_at"]

    def __str__(self) -> str:
        return str(self.id)


class BaseImageAssetFile(models.Model):
    id: models.AutoField[int, int] = models.AutoField(primary_key=True)
    file: models.ImageField = models.ImageField(blank=True, null=True)
    filename: models.CharField[str, str] = models.CharField(max_length=120, blank=True)
    filename_shorter: models.CharField[str, str] = models.CharField(max_length=30, blank=True)
    content_type: models.CharField[str, str] = models.CharField(max_length=20)
    format: models.CharField[str, str] = models.CharField(max_length=10, blank=True)
    format_description: models.CharField[str, str] = models.CharField(max_length=50, blank=True)
    size: models.IntegerField[Optional[int], int] = models.IntegerField(null=True)
    width: models.IntegerField[Optional[int], int] = models.IntegerField(null=True)
    height: models.IntegerField[Optional[int], int] = models.IntegerField(null=True)
    aspect_ratio: models.DecimalField[Optional[Decimal], Decimal] = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
    )
    color_mode: models.CharField[str, str] = models.CharField(max_length=10)
    exif_data: models.JSONField = models.JSONField()

    class Meta:
        abstract: bool = True

    def __str__(self) -> str:
        return str(self.id)
