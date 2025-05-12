from decimal import Decimal

from django.core.files.base import ContentFile
from ninja import Schema
from pydantic import ConfigDict


class ImageFileInfo(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    content_file: ContentFile[bytes]
    filename: str
    filename_shorter: str
    file_format: str
    file_format_description: str
    size: int
    width: int
    height: int
    aspect_ratio: Decimal
    color_mode: str
    exif_data: dict[str, str]
