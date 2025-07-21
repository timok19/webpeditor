from datetime import datetime
from typing import Optional

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from webpeditor_app.infrastructure.database.utils import generate_id


class AppUser(models.Model):
    id: models.CharField[str] = models.CharField(primary_key=True, default=generate_id, editable=False, max_length=128)
    session_key: models.CharField[Optional[str]] = models.CharField(max_length=128, null=True)
    session_key_expiration_date: models.DateTimeField[datetime] = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        verbose_name: str = _("App User")
        verbose_name_plural: str = _("App Users")
