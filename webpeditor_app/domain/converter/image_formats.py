from enum import StrEnum
from typing import Union


class RasterImageFormats(StrEnum):
    JPEG = "JPEG"
    BMP = "BMP"
    TIFF = "TIFF"


class RasterImageFormatsWithAlphaChannel(StrEnum):
    WEBP = "WEBP"
    PNG = "PNG"
    GIF = "GIF"
    ICO = "ICO"


type AllRasterImageFormats = Union[RasterImageFormats, RasterImageFormatsWithAlphaChannel]
