import os

from typing import Final, Optional, Union
from PIL import Image
from PIL.ImageFile import ImageFile
from io import BytesIO

from expression import Option
from types_linq import Enumerable

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
        self.__mode_rgb: Final[str] = "RGB"
        self.__mode_rgba: Final[str] = "RGBA"
        self.__mode_palette: Final[str] = "P"

    def get_info(self, image: ImageFile) -> ContextResult[ImageFileInfo]:
        return self.__image_file_utility.get_file_info(image)

    def convert_image(
        self,
        image: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFileInfo]:
        return (
            self.__update_filename(image, options)
            .bind(lambda img_new_filename: self.__convert_color_mode(img_new_filename, options))
            .map(lambda img_converted_color_mode: self.__convert_format(img_converted_color_mode, options))
            .bind(self.__get_info_and_close)
        )

    def __update_filename(
        self,
        image_file: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile]:
        return ContextResult[ImageFile].from_result(
            Option[str]
            .of_optional(image_file.filename)
            .to_result(ErrorContext.server_error("Image file has no filename"))
            .bind(self.__image_file_utility.normalize_filename)
            .map(lambda normalized_filename: Enumerable(os.path.splitext(normalized_filename)).first2(""))
            .map(lambda basename: f"webpeditor_{basename}.{options.output_format.lower()}")
            .bind(lambda new_filename: self.__image_file_utility.update_filename(image_file, new_filename))
        )

    def __convert_color_mode(
        self,
        image: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile]:
        if image.format is None:
            error = ErrorContext.server_error("Unable to convert image color. Invalid image format")
            return ContextResult[ImageFile].failure(error)

        filename = image.filename

        # Determine if source and target formats support alpha
        source_has_alpha = (
            image.mode == self.__mode_rgba or image.format.upper() in ImageConverterOutputFormatsWithAlphaChannel
        )
        target_has_alpha = options.output_format in ImageConverterOutputFormatsWithAlphaChannel

        # Determine the appropriate conversion based on image mode and alpha support
        if image.mode in self.__mode_palette:
            # For palette mode, convert to RGBA or RGB based on target format
            target_mode = self.__mode_rgba if target_has_alpha else self.__mode_rgb
            converted_image = image.convert(target_mode)
        elif source_has_alpha and target_has_alpha:
            # Both source and target support alpha, keep RGBA
            converted_image = image.convert(self.__mode_rgba)
        elif source_has_alpha:
            # Source has alpha but target doesn't, convert to RGB
            converted_image = self.__to_rgb(image)
        else:
            # Source doesn't have alpha, convert to RGB
            converted_image = image.convert(self.__mode_rgb)

        buffer = BytesIO()
        converted_image.save(buffer, format=image.format)

        return ContextResult[ImageFile].success(self.__to_image_file(buffer, filename))

    def __to_rgb(self, rgba_image: Image.Image) -> Image.Image:
        white_color = (255, 255, 255, 255)
        white_background: Image.Image = Image.new(mode=self.__mode_rgba, size=rgba_image.size, color=white_color)
        # Merge RGBA into RGB with a white background
        return Image.alpha_composite(white_background, rgba_image).convert(self.__mode_rgb)

    def __convert_format(self, image: ImageFile, options: ConversionRequest.Options) -> ImageFile:
        filename = image.filename
        buffer = BytesIO()

        match options.output_format:
            case ImageConverterAllOutputFormats.JPEG:
                # Convert palette mode (P) to RGB before saving as JPEG
                image_to_save = image.convert(self.__mode_rgb) if image.mode == self.__mode_palette else image
                image_to_save.save(
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

        return self.__to_image_file(buffer, filename)

    @staticmethod
    def __to_image_file(buffer: BytesIO, filename: Optional[Union[str, bytes]]) -> ImageFile:
        # Set pointer to start
        buffer.seek(0)
        result = Image.open(buffer)
        result.filename = filename
        return result

    def __get_info_and_close(self, image: ImageFile) -> ContextResult[ImageFileInfo]:
        return self.__image_file_utility.get_file_info(image).bind(
            lambda info: self.__image_file_utility.close_file(image).map(lambda _: info)
        )
