from enum import StrEnum


class ImageConverterAllOutputFormats(StrEnum):
    JPEG = "JPEG"
    BMP = "BMP"
    TIFF = "TIFF"
    WEBP = "WEBP"
    PNG = "PNG"
    GIF = "GIF"
    ICO = "ICO"


class ImageConverterOutputFormats(StrEnum):
    JPEG = "JPEG"
    BMP = "BMP"
    TIFF = "TIFF"


class ImageConverterOutputFormatsWithAlphaChannel(StrEnum):
    WEBP = "WEBP"
    PNG = "PNG"
    GIF = "GIF"
    ICO = "ICO"
