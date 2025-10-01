from decimal import Decimal
from enum import StrEnum
from typing import Self

from ninja import Schema, UploadedFile
from pydantic import ConfigDict

from webpeditor_app.infrastructure.database.models.base import BaseImageAssetFile


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


class ConversionRequest(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    files: list[UploadedFile]
    options: "Options"

    class Options(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        output_format: ImageConverterAllOutputFormats
        quality: int

    @classmethod
    def create(cls, files: list[UploadedFile], output_format: ImageConverterAllOutputFormats, quality: int) -> "ConversionRequest":
        return cls(files=files, options=cls.Options(output_format=output_format, quality=quality))


class ConversionResponse(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    original_data: "ImageData"
    converted_data: "ImageData"

    @classmethod
    def create(cls, original_data: "ImageData", converted_data: "ImageData") -> Self:
        return cls(original_data=original_data, converted_data=converted_data)

    class ImageData(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

        url: str
        filename: str
        filename_shorter: str
        content_type: str
        format: str
        format_description: str
        size: int
        width: int
        height: int
        aspect_ratio: Decimal
        color_mode: str
        exif_data: dict[str, str]

        @classmethod
        def from_asset(cls, asset_file: BaseImageAssetFile) -> Self:
            return cls(
                url=asset_file.file_url,
                filename=asset_file.filename,
                filename_shorter=asset_file.filename_shorter,
                content_type=asset_file.content_type,
                format=asset_file.format,
                format_description=asset_file.format_description,
                size=asset_file.size or 0,
                width=asset_file.width or 0,
                height=asset_file.height or 0,
                aspect_ratio=asset_file.aspect_ratio or Decimal(),
                color_mode=asset_file.color_mode,
                exif_data=asset_file.exif_data,
            )
