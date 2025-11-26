from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class ImageAsset(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: UUID
    user_id: str
    created_at: datetime


class ImageAssetFile(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: UUID
    file_url: HttpUrl
    filename: str
    filename_shorter: str
    content_type: str
    format: str
    format_description: str
    size: int
    width: int
    height: int
    aspect_ratio: Decimal
    color_mode: str
    exif_data: dict[str, Any]
