from datetime import datetime
from typing import Optional

from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class OriginalImage(Document):
    image_id: Optional[UUID] = Field(default_factory=uuid4, alias="_id")
    image_name: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=255)
    image_url: str = Field(...)
    user_id: Optional[UUID] = Field(default_factory=uuid4)
    session_key: str = Field(...)
    session_key_expiration_date: Optional[datetime] = Field(default=datetime.utcnow())
    created_at: Optional[datetime] = Field(default=datetime.utcnow())

# TODO: Rewrite models for async MongoEngine
class EditedImage(Document):
    image_id: Optional[UUID] = Field(default_factory=uuid4, alias="_id")
    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=255, default="")
    content_type = models.CharField(max_length=255)
    image_url = models.CharField(max_length=350, default="")
    user_id = models.CharField(max_length=32, null=True)
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)


class ConvertedImage(Document):
    user_id = models.CharField(max_length=32, null=True)
    image_set = models.JSONField()
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
