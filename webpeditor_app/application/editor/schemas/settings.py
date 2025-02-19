from enum import StrEnum
from typing import Final

from ninja import Schema
from pydantic import ConfigDict


class ImageEditorAllOutputFormats(StrEnum):
    JPEG = "JPEG"
    JPG = "JPG"
    JFIF = "JFIF"
    BMP = "BMP"
    TIFF = "TIFF"
    WEBP = "WEBP"
    PNG = "PNG"
    ICO = "ICO"
    GIF = "GIF"


class ImageEditorOutputFormats(StrEnum):
    JPEG = "JPEG"
    JPG = "JPG"
    JFIF = "JFIF"
    BMP = "BMP"
    TIFF = "TIFF"


class ImageEditorOutputFormatsWithAlphaChannel(StrEnum):
    WEBP = "WEBP"
    PNG = "PNG"
    ICO = "ICO"
    GIF = "GIF"


class _ImageEditorSettings(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    max_file_size: Final[int] = 6_291_456


IMAGE_EDITOR_SETTINGS: _ImageEditorSettings = _ImageEditorSettings()
