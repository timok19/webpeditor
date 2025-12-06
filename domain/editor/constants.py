from enum import StrEnum
from typing import Final, final

from domain.common.constants import ImageFilePropertyConstants


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
