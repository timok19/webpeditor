from enum import StrEnum
from typing import Final

from ninja import Schema
from pydantic import ConfigDict


class ImageConverterAllOutputFormats(StrEnum):
    JPEG = "JPEG"
    BMP = "BMP"
    TIFF = "TIFF"
    WEBP = "WEBP"
    PNG = "PNG"
    GIF = "GIF"
    ICO = "ICO"


class ImageConverterOutputFormats(StrEnum):
    JPEG = "JPEG"
    BMP = "BMP"
    TIFF = "TIFF"


class ImageConverterOutputFormatsWithAlphaChannel(StrEnum):
    WEBP = "WEBP"
    PNG = "PNG"
    GIF = "GIF"
    ICO = "ICO"


class _ImageConverterSettings(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    min_quality: Final[int] = 5
    max_quality: Final[int] = 100
    max_file_size: Final[int] = 6_291_456
    max_total_files_count: Final[int] = 10


IMAGE_CONVERTER_SETTINGS: _ImageConverterSettings = _ImageConverterSettings()
