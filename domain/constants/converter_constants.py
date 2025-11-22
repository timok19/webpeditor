from enum import StrEnum
from typing import final, Final

from domain.constants.image_file_property_constants import ImageFilePropertyConstants


@final
class ConverterConstants(ImageFilePropertyConstants):
    class ImageFormats(StrEnum):
        JPEG = "JPEG"
        BMP = "BMP"
        TIFF = "TIFF"

    class ImageFormatsWithAlphaChannel(StrEnum):
        WEBP = "WEBP"
        PNG = "PNG"
        GIF = "GIF"
        ICO = "ICO"

    MIN_QUALITY: Final[int] = 5
    MAX_QUALITY: Final[int] = 100
    MAX_FILE_SIZE: Final[int] = 6_291_456
    MAX_FILES_LIMIT: Final[int] = 10
    MAX_IMAGE_DIMENSIONS: Final[int] = 4000
    SAFE_AREA: Final[int] = 1_000_000
    ALL_IMAGE_FORMATS: Final[frozenset[str]] = frozenset[str](
        {
            *(image_format.value for image_format in ImageFormats),
            *(image_format.value for image_format in ImageFormatsWithAlphaChannel),
        }
    )
