from io import BytesIO
from typing import Any, Final, Union, cast

from expression import Option
from PIL import Image, ImageFile

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.converter.commands.schemas.conversion import ConversionRequest
from application.converter.services.abc.image_file_converter_abc import ImageFileConverterABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext, as_awaitable_result
from domain.converter.constants import ConverterConstants

type _StrOrBytes = Union[str, bytes]


class ImageFileConverter(ImageFileConverterABC):
    def __init__(self, image_file_service: ImageFileServiceABC, filename_service: FilenameServiceABC, logger: LoggerABC) -> None:
        self.__image_file_service: Final[ImageFileServiceABC] = image_file_service
        self.__filename_service: Final[FilenameServiceABC] = filename_service
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aconvert(self, file: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
        return await (
            ContextResult[_StrOrBytes]
            .from_result(Option[_StrOrBytes].of_optional(file.filename).to_result(ErrorContext.server_error("Image file has no filename")))
            .bind(self.__filename_service.get_basename)
            .map(lambda basename: f"webpeditor_{basename}.{options.output_format.lower()}")
            .bind(lambda new_filename: self.__image_file_service.set_filename(file, new_filename))
            .abind(lambda updated_file: self.__aconvert(updated_file, options))
        )

    @as_awaitable_result
    async def __aconvert(
        self,
        file: ImageFile.ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile.ImageFile]:
        if file.format is None:
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.server_error("Unable to convert image. Invalid image format"))

        filename = file.filename

        source_has_alpha = file.mode == ConverterConstants.RGBA_MODE or file.format in ConverterConstants.ImageFormatsWithAlphaChannel
        target_has_alpha = options.output_format in ConverterConstants.ImageFormatsWithAlphaChannel

        target_mode = ConverterConstants.RGBA_MODE if target_has_alpha else ConverterConstants.RGB_MODE

        # Optimize the color mode conversion
        if file.mode != target_mode or file.mode == ConverterConstants.PALETTE_MODE:
            file = cast(ImageFile.ImageFile, file.convert(target_mode))
        elif source_has_alpha and not target_has_alpha:
            file = cast(ImageFile.ImageFile, self.__to_rgb(file))

        file_bytes = self.__convert_format(file, options)
        buffered_file = BytesIO(file_bytes)

        converted = Image.open(buffered_file)
        # Force-load the image so the buffer can be released safely
        converted.load()
        converted.filename = filename
        buffered_file.close()

        return ContextResult[ImageFile.ImageFile].success(converted)

    def __convert_format(self, image: Image.Image, options: ConversionRequest.Options) -> bytes:
        save_args: dict[str, Any] = {"quality": options.quality, "exif": image.getexif(), "optimize": True}

        if options.output_format == ConverterConstants.ImageFormats.JPEG:
            if image.mode != ConverterConstants.RGB_MODE:
                image = image.convert(ConverterConstants.RGB_MODE)
            save_args.update({"subsampling": 0 if options.quality >= 95 else 2, "progressive": self.__is_large_image(image)})
        elif options.output_format == ConverterConstants.ImageFormatsWithAlphaChannel.PNG:
            save_args.update({"compress_level": 6 if self.__is_large_image(image) else 9})
        elif options.output_format == ConverterConstants.ImageFormatsWithAlphaChannel.WEBP:
            save_args.update({"method": 4 if options.quality < 90 else 5, "lossless": options.quality >= 98})
        elif options.output_format == ConverterConstants.ImageFormats.TIFF:
            save_args.update({"compression": "jpeg" if image.mode == ConverterConstants.RGB_MODE else "tiff_deflate"})

        with BytesIO() as buffer:
            image.save(buffer, options.output_format, **save_args)
            return buffer.getvalue()

    @staticmethod
    def __is_large_image(image: Image.Image) -> bool:
        return image.width * image.height > ConverterConstants.SAFE_AREA

    @staticmethod
    def __to_rgb(rgba_image: Image.Image) -> Image.Image:
        white_color = (255, 255, 255, 255)
        white_background = Image.new(mode=ConverterConstants.RGBA_MODE, size=rgba_image.size, color=white_color)
        # Ensure rgba_image is in RGBA mode before compositing
        if rgba_image.mode != ConverterConstants.RGBA_MODE:
            rgba_image = rgba_image.convert(ConverterConstants.RGBA_MODE)
        # Merge RGBA into RGB with a white background
        return Image.alpha_composite(white_background, rgba_image).convert(ConverterConstants.RGB_MODE)
