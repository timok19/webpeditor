from datetime import datetime
from typing import Optional, List
from typing_extensions import TypedDict
from uuid import UUID, uuid4

from PIL.Image import Exif
from beanie import Document
from pydantic import Field, BaseConfig


class ImageData(TypedDict):
    content_type: str
    format: str
    file_size: str
    color_mode: str
    exif_data: Exif


class ImageSet(TypedDict):
    image_id: UUID
    short_image_name: str
    public_id: str
    image_name: str
    image_url: str
    original_image_data: ImageData
    converted_image_data: ImageData


class ConvertedImage(Document):
    user_id: Optional[UUID] = Field(default_factory=uuid4)
    image_set: List[ImageSet] = Field(...)
    session_key: str = Field(...)
    session_key_expiration_date: Optional[datetime] = Field(default=datetime.utcnow())
    created_at: Optional[datetime] = Field(default=datetime.utcnow())

    class Config(BaseConfig):
        validate_all = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
