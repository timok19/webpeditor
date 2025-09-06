import hashlib
import secrets
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class APIKey(models.Model):
    email: models.EmailField[str] = models.EmailField(max_length=50, unique=True)
    key_hash: models.CharField[str] = models.CharField(max_length=128, unique=True)
    created_at: models.DateTimeField[datetime] = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")

    @staticmethod
    def create_api_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()
