from datetime import datetime
from django.db import models
from django.utils import timezone


class APIKey(models.Model):
    email: models.EmailField[str] = models.EmailField(max_length=50, unique=True)
    key_hash: models.CharField[str] = models.CharField(max_length=128, unique=True)
    created_at: models.DateTimeField[datetime] = models.DateTimeField(default=timezone.now)
