from datetime import datetime
from typing import Optional

from django.db import models
from django.utils import timezone
from names_generator import generate_name
from uuid_utils import uuid7


def generate_id() -> str:
    return f"{generate_name(style='hyphen')}-{uuid7()}"


class AppUser(models.Model):
    id: models.CharField[str, str] = models.CharField(primary_key=True, default=generate_id, editable=False)
    session_key: models.CharField[Optional[str], str] = models.CharField(max_length=120, null=True)
    session_key_expiration_date: models.DateTimeField[datetime, datetime] = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(self.id)
