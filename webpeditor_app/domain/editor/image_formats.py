from enum import StrEnum
from typing import Union


class RasterImageFormats(StrEnum):
    JPEG = "JPEG"
    JPG = "JPG"
    JFIF = "JFIF"
    BMP = "BMP"
    TIFF = "TIFF"


class RasterImageFormatsWithAlphaChannel(StrEnum):
    WEBP = "WEBP"
    PNG = "PNG"
    ICO = "ICO"
    GIF = "GIF"


type AllRasterImageFormats = Union[RasterImageFormats, RasterImageFormatsWithAlphaChannel]
