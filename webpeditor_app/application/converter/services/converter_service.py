import os

from typing import Final
from PIL import Image
from PIL.ImageFile import ImageFile
from io import BytesIO

from webpeditor_app.application.converter.abc.converter_service_abc import ConverterServiceABC
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import ContextResult, ErrorContext
from webpeditor_app.application.converter.schemas.output_formats import (
    ImageConverterAllOutputFormats,
    ImageConverterOutputFormatsWithAlphaChannel,
)


class ConverterService(ConverterServiceABC):
    def __init__(self, image_file_utility: ImageFileUtilityABC) -> None:
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility

    def get_info(self, image: ImageFile) -> ContextResult[ImageFileInfo]:
        return (
            self.__image_file_utility.normalize_filename(image.filename)
            .bind(lambda filename: self.__image_file_utility.update_filename(image, filename))
            .bind(self.__image_file_utility.get_file_info)
        )

    def convert_image(
        self,
        image: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFileInfo]:
        return (
            self.__image_file_utility.normalize_filename(image.filename)
            .bind(lambda filename: self.__update_filename(image, filename, options))
            .bind(lambda img: self.__convert_color_mode(img, options))
            .map(lambda img: self.__convert_format(img, options))
            .bind(self.__image_file_utility.get_file_info)
        )

    def __update_filename(
        self,
        image_file: ImageFile,
        filename: str,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile]:
        basename, _ = os.path.splitext(filename)
        new_filename = f"webpeditor_{basename}.{options.output_format.lower()}"
        return self.__image_file_utility.update_filename(image_file, new_filename)

    def __convert_color_mode(
        self,
        image: Image.Image,
        options: ConversionRequest.Options,
    ) -> ContextResult[Image.Image]:
        if image.format is None:
            return ContextResult[Image.Image].failure(
                ErrorContext.server_error("Unable to convert image color. Invalid image format")
            )

        if image.format.upper() not in ImageConverterOutputFormatsWithAlphaChannel:
            return ContextResult[Image.Image].success(image.convert("RGB"))

        rgba_image = image.convert("RGBA")

        if options.output_format in ImageConverterOutputFormatsWithAlphaChannel:
            return ContextResult[Image.Image].success(rgba_image)

        return ContextResult[Image.Image].success(self.__to_rgb(rgba_image))

    @staticmethod
    def __to_rgb(rgba_image: Image.Image) -> Image.Image:
        white_color = (255, 255, 255, 255)
        white_background: Image.Image = Image.new(mode="RGBA", size=rgba_image.size, color=white_color)
        # Merge RGBA into RGB with a white background
        return Image.alpha_composite(white_background, rgba_image).convert("RGB")

    @staticmethod
    def __convert_format(image: Image.Image, options: ConversionRequest.Options) -> ImageFile:
        buffer = BytesIO()

        match options.output_format:
            case ImageConverterAllOutputFormats.JPEG:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.JPEG,
                    quality=options.quality,
                    subsampling=0 if options.quality == 100 else 2,
                    exif=image.getexif(),
                    optimize=True,
                )
            case ImageConverterAllOutputFormats.TIFF:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.TIFF,
                    quality=options.quality,
                    exif=image.getexif(),
                    optimize=True,
                    compression="jpeg" if image.format == ImageConverterAllOutputFormats.JPEG else None,
                )
            case ImageConverterAllOutputFormats.BMP:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.BMP,
                    bitmap_format="bmp",
                    optimize=True,
                )
            case ImageConverterAllOutputFormats.PNG:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.PNG,
                    bitmap_format="png",
                    exif=image.getexif(),
                    optimize=True,
                )
            case _:
                image.save(
                    buffer,
                    format=options.output_format,
                    quality=options.quality,
                    exif=image.getexif(),
                    optimize=True,
                )

        # Set pointer to start
        buffer.seek(0)
        return Image.open(buffer)
