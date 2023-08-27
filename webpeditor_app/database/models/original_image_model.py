from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field, BaseModel, BaseConfig


class ImageModel(BaseModel):
    image_id: Optional[UUID] = Field(default_factory=uuid4, alias="_id")
    image_name: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=255)
    image_url: str = Field(...)
    user_id: Optional[UUID] = Field(default_factory=uuid4)
    session_key: str = Field(...)
    session_key_expiration_date: Optional[datetime] = Field(default=datetime.utcnow())
    created_at: Optional[datetime] = Field(default=datetime.utcnow())


class OriginalImage(Document):
    image: ImageModel

    class Config(BaseConfig):
        validate_all = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
