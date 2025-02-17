from decimal import Decimal

from PIL.ImageFile import ImageFile
from django.core.files.base import ContentFile
from ninja import Schema
from pydantic import ConfigDict


class ImageFileInfo(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    image_file: ImageFile
    content_file: ContentFile
    filename: str
    file_format: str
    file_format_description: str
    size: int
    resolution: tuple[int, int]
    aspect_ratio: Decimal
    color_mode: str
    exif_data: dict[str, str]
