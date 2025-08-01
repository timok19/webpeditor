import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from django.db import models
from django.utils import timezone


class BaseImageAsset(models.Model):
    id: models.UUIDField[uuid.UUID] = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at: models.DateTimeField[datetime] = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract: bool = True
        ordering: list[str] = ["-created_at"]

    def __str__(self) -> str:
        return str(self.id)


class BaseImageAssetFile(models.Model):
    id: models.UUIDField[uuid.UUID] = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_url: models.URLField[str] = models.URLField(blank=True)
    filename: models.CharField[str] = models.CharField(max_length=120, blank=True)
    filename_shorter: models.CharField[str] = models.CharField(max_length=30, blank=True)
    content_type: models.CharField[str] = models.CharField(max_length=20)
    format: models.CharField[str] = models.CharField(max_length=10, blank=True)
    format_description: models.CharField[str] = models.CharField(max_length=50, blank=True)
    size: models.IntegerField[Optional[int]] = models.IntegerField(null=True)
    width: models.IntegerField[Optional[int]] = models.IntegerField(null=True)
    height: models.IntegerField[Optional[int]] = models.IntegerField(null=True)
    aspect_ratio: models.DecimalField[Optional[Decimal]] = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
    )
    color_mode: models.CharField[str] = models.CharField(max_length=10)
    exif_data: models.JSONField[Any] = models.JSONField()

    class Meta:
        abstract: bool = True

    def __str__(self) -> str:
        return str(self.id)
