from datetime import datetime
from typing import Optional

from django.utils import timezone
from django.db import models
from django_extensions.db.fields import ShortUUIDField


class AppUser(models.Model):
    id: models.CharField[str] = ShortUUIDField(primary_key=True, editable=False)
    session_key: models.CharField[Optional[str]] = models.CharField(max_length=120, null=True)
    session_key_expiration_date: models.DateTimeField[datetime] = models.DateTimeField(default=timezone.now)
