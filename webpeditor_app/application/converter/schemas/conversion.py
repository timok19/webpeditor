from decimal import Decimal

from ninja import Schema, UploadedFile
from pydantic import ConfigDict

from webpeditor_app.application.converter.schemas.output_formats import ImageConverterAllOutputFormats
from webpeditor_app.models.base import BaseImageAssetFile


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

    original_data: "ImageData"
    converted_data: "ImageData"

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
        def from_asset_file(cls, asset_file: BaseImageAssetFile) -> "ConversionResponse.ImageData":
            return cls(
                url=asset_file.file_url,
                filename=str(asset_file.filename),
                filename_shorter=str(asset_file.filename_shorter),
                content_type=str(asset_file.content_type),
                format=str(asset_file.format),
                format_description=str(asset_file.format_description),
                size=asset_file.size or 0,
                width=asset_file.width or 0,
                height=asset_file.height or 0,
                aspect_ratio=asset_file.aspect_ratio or Decimal(),
                color_mode=str(asset_file.color_mode),
                exif_data=asset_file.exif_data,
            )
