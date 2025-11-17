from enum import StrEnum
from typing import Final


class RasterImageFormats(StrEnum):
    JPEG = "JPEG"
    BMP = "BMP"
    TIFF = "TIFF"


class RasterImageFormatsWithAlphaChannel(StrEnum):
    WEBP = "WEBP"
    PNG = "PNG"
    GIF = "GIF"
    ICO = "ICO"


ALL_RASTER_IMAGE_FORMATS: Final[frozenset[str]] = frozenset[str](
    {
        *(image_format.value for image_format in RasterImageFormats),
        *(image_format.value for image_format in RasterImageFormatsWithAlphaChannel),
    }
)
