from typing import final, Final

from domain.constants.image_file_property_constants import ImageFilePropertyConstants
from enum import StrEnum


@final
class EditorConstants(ImageFilePropertyConstants):
    class ImageFormats(StrEnum):
        JPEG = "JPEG"
        JPG = "JPG"
        JFIF = "JFIF"
        BMP = "BMP"
        TIFF = "TIFF"

    class ImageFormatsWithAlphaChannel(StrEnum):
        WEBP = "WEBP"
        PNG = "PNG"
        ICO = "ICO"
        GIF = "GIF"

    MAX_FILE_SIZE: Final[int] = 6_291_456
