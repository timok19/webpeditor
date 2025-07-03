from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ImageFileInfo(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    filename: str
    filename_shorter: str
    file_basename: str
    file_format: str
    file_format_description: str
    file_content: bytes
    size: int
    width: int
    height: int
    aspect_ratio: Decimal
    color_mode: str
    exif_data: dict[str, str]
