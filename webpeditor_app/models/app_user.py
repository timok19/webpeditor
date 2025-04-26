from datetime import datetime
from typing import Optional

from django.utils import timezone
from django.db import models
from django_extensions.db.fields import ShortUUIDField


class AppUser(models.Model):
    id: models.CharField[str, str] = ShortUUIDField(primary_key=True, editable=False)
    session_key: models.CharField[Optional[str], str] = models.CharField(max_length=120, null=True)
    session_key_expiration_date: models.DateTimeField[datetime, datetime] = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(self.id)
