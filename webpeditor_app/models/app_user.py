from django.utils import timezone
from django.db import models
from django_extensions.db.fields import ShortUUIDField


class AppUser(models.Model):
    id = ShortUUIDField(primary_key=True, editable=False)
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
