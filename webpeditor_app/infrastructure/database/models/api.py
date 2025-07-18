from datetime import datetime
from django.db import models
from django.utils import timezone


# TODO: make sure that APIKey is being added into database via Django Admin
class APIKey(models.Model):
    email: models.EmailField[str, str] = models.EmailField(max_length=50, unique=True)
    key_hash: models.CharField[str, str] = models.CharField(max_length=128, unique=True)
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(default=timezone.now)
