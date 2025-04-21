from enum import StrEnum


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
