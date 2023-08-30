from enum import Enum
from typing import Literal


class RGBImageFormat(Enum):
    JPEG = "JPEG"
    JPG = "JPG"
    JFIF = "JFIF"
    BMP = "BMP"
    TIFF = "TIFF"


class RGBAImageFormat(Enum):
    WEBP = "WEBP"
    PNG = "PNG"
    ICO = "ICO"
    GIF = "GIF"


AllowedImageFormats = Literal[
    RGBImageFormat.JPEG,
    RGBImageFormat.JPG,
    RGBImageFormat.JFIF,
    RGBImageFormat.BMP,
    RGBImageFormat.TIFF,
    RGBAImageFormat.WEBP,
    RGBAImageFormat.PNG,
    RGBAImageFormat.ICO,
    RGBAImageFormat.GIF,
]
