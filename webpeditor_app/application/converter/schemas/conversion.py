from decimal import Decimal

from ninja import Schema, UploadedFile
from pydantic import ConfigDict

from webpeditor_app.application.converter.schemas.output_formats import ImageConverterAllOutputFormats
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo


class ConversionRequest(Schema):
    class Options(Schema):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        output_format: ImageConverterAllOutputFormats
        quality: int

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    files: list[UploadedFile]
    options: Options

    @staticmethod
    def create(
        files: list[UploadedFile],
        output_format: ImageConverterAllOutputFormats,
        quality: int,
    ) -> "ConversionRequest":
        return ConversionRequest(
            files=files,
            options=ConversionRequest.Options(
                output_format=output_format,
                quality=quality,
            ),
        )


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
        width: int
        height: int
        aspect_ratio: Decimal
        color_mode: str
        exif_data: dict[str, str]


class OriginalAndConvertedImageFileInfo(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", arbitrary_types_allowed=True)

    original: ImageFileInfo
    converted: ImageFileInfo
