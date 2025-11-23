from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import UUID

from ninja import Schema, UploadedFile
from pydantic import ConfigDict


class ConversionRequest(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    files: list[UploadedFile]
    options: "Options"

    class Options(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        output_format: "OutputFormats"
        quality: int

        class OutputFormats(StrEnum):
            JPEG = "JPEG"
            BMP = "BMP"
            TIFF = "TIFF"
            WEBP = "WEBP"
            PNG = "PNG"
            GIF = "GIF"
            ICO = "ICO"

    @classmethod
    def create(cls, files: list[UploadedFile], output_format: Options.OutputFormats, quality: int) -> Self:
        return cls(files=files, options=cls.Options(output_format=output_format, quality=quality))


class ConversionResponse(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    original_image_data: "ImageData"
    converted_image_data: "ImageData"

    @classmethod
    def create(cls, original_image_data: "ImageData", converted_image_data: "ImageData") -> Self:
        return cls(original_image_data=original_image_data, converted_image_data=converted_image_data)

    class ImageData(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

        id: UUID
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
