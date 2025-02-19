from decimal import Decimal

from ninja import Schema, UploadedFile
from pydantic import ConfigDict

from webpeditor_app.application.converter.schemas.settings import ImageConverterAllOutputFormats


class ConversionRequest(Schema):
    class Options(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        output_format: ImageConverterAllOutputFormats
        quality: int

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    files: list[UploadedFile]
    options: Options


class ConversionResponse(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    original_image_data: "ImageData"
    converted_image_data: "ImageData"

    class ImageData(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

        url: str
        filename: str
        filename_shorter: str
        content_type: str
        format: str
        format_description: str
        size: int
        resolution: tuple[int, int]
        aspect_ratio: Decimal
        color_mode: str
        exif_data: dict[str, str]
