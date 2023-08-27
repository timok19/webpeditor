from enum import Enum
from typing import Union


class BaseImageFormat(Enum):
    @classmethod
    def from_str(cls, image_format: str):
        try:
            return cls[image_format]
        except KeyError:
            return None


class RGBImageFormat(BaseImageFormat):
    JPEG = "JPEG"
    JPG = "JPG"
    JFIF = "JFIF"
    BMP = "BMP"
    TIFF = "TIFF"


class RGBAImageFormat(BaseImageFormat):
    WEBP = "WEBP"
    PNG = "PNG"
    ICO = "ICO"
    GIF = "GIF"


AllowedImageFormats = Union[
    *RGBImageFormat,
    *RGBAImageFormat,
]
