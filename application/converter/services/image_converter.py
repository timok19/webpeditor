import math
from io import BytesIO
from typing import Any, Final, cast

from expression import Option
from PIL import Image, ImageFile

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.converter.commands.schemas.conversion import ConversionRequest
from application.converter.services.abc.image_converter_abc import ImageConverterABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext, as_awaitable_result
from domain.converter.constants import ImageConverterConstants
from domain.converter.formats import RasterImageFormats, RasterImageFormatsWithAlphaChannel


try:
    import multiprocessing

    # Enable truncated image processing for better memory usage
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # Enable chunked processing to reduce memory usage and improve performance
    # Set PIL to use multiple cores when available
    Image.core.set_alignment(32)
    Image.core.set_blocks_max(multiprocessing.cpu_count() * 2)
except (ImportError, AttributeError):
    pass


class ImageConverter(ImageConverterABC):
    def __init__(self, image_file_utility: ImageFileServiceABC, filename_utility: FilenameServiceABC, logger: LoggerABC) -> None:
        self.__image_file_utility: Final[ImageFileServiceABC] = image_file_utility
        self.__filename_utility: Final[FilenameServiceABC] = filename_utility
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aconvert(self, file: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
        return await self.__add_filename_prefix(file, options).abind(lambda image_file: self.__aconvert_image(image_file, options))

    def __add_filename_prefix(
        self,
        image_file: ImageFile.ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile.ImageFile]:
        return ContextResult[ImageFile.ImageFile].from_result(
            Option[str]
            .of_optional(image_file.filename)
            .to_result(ErrorContext.server_error("Image file has no filename"))
            .bind(self.__filename_utility.normalize)
            .bind(self.__filename_utility.get_basename)
            .map(lambda basename: f"webpeditor_{basename}.{options.output_format.lower()}")
            .bind(lambda new_filename: self.__image_file_utility.update_filename(image_file, new_filename))
        )

    @as_awaitable_result
    async def __aconvert_image(
        self,
        image_file: ImageFile.ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile.ImageFile]:
        if image_file.format is None:
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.server_error("Unable to convert image. Invalid image format"))

        # Resize large images to improve performance
        resized = self.__resize_image(image_file)

        source_has_alpha = resized.mode == ImageConverterConstants.RGBA_MODE or resized.format in RasterImageFormatsWithAlphaChannel
        target_has_alpha = options.output_format in RasterImageFormatsWithAlphaChannel

        target_mode = ImageConverterConstants.RGBA_MODE if target_has_alpha else ImageConverterConstants.RGB_MODE

        # Optimize the color mode conversion
        if resized.mode == ImageConverterConstants.PALETTE_MODE:
            resized = resized.convert(target_mode)
        elif source_has_alpha and not target_has_alpha:
            resized = self.__to_rgb(resized)
        elif resized.mode != target_mode:
            resized = resized.convert(target_mode)

        converted = Image.open(BytesIO(self.__convert_format(resized, options)))
        # Force-load the image so the buffer can be released safely
        converted.load()
        converted.filename = image_file.filename

        return ContextResult[ImageFile.ImageFile].success(converted)

    @staticmethod
    def __resize_image(image: ImageFile.ImageFile) -> ImageFile.ImageFile:
        if image.width <= ImageConverterConstants.MAX_IMAGE_DIMENSIONS and image.height <= ImageConverterConstants.MAX_IMAGE_DIMENSIONS:
            return image

        # Calculate new dimensions while preserving an aspect ratio
        if image.width > image.height:
            new_width = ImageConverterConstants.MAX_IMAGE_DIMENSIONS
            new_height = math.ceil(image.height * (ImageConverterConstants.MAX_IMAGE_DIMENSIONS / image.width))
        else:
            new_height = ImageConverterConstants.MAX_IMAGE_DIMENSIONS
            new_width = math.ceil(image.width * (ImageConverterConstants.MAX_IMAGE_DIMENSIONS / image.height))

        # Use BICUBIC instead of LANCZOS for faster resizing with acceptable quality
        # BICUBIC is about 30-40% faster than LANCZOS with minimal quality difference for downsampling
        resized_image = cast(ImageFile.ImageFile, image.resize((new_width, new_height), Image.Resampling.BICUBIC))
        resized_image.format = image.format
        resized_image.filename = image.filename

        return resized_image

    def __convert_format(self, image: Image.Image, options: ConversionRequest.Options) -> bytes:
        save_args: dict[str, Any] = {"quality": options.quality, "exif": image.getexif(), "optimize": True}

        if options.output_format == RasterImageFormats.JPEG:
            # Ensure RGB mode for JPEG
            if image.mode != ImageConverterConstants.RGB_MODE:
                image = image.convert(ImageConverterConstants.RGB_MODE)

            save_args.update(
                {
                    "subsampling": 0 if options.quality >= 95 else 2,  # Better subsampling for high quality
                    "progressive": self.__is_large_image(image),  # Progressive only for large images for better performance
                }
            )

        elif options.output_format == RasterImageFormatsWithAlphaChannel.PNG:
            # Adjust compression level based on image size
            # Higher compression for smaller images, lower for larger ones for better performance
            save_args.update({"compress_level": 6 if self.__is_large_image(image) else 9})

        elif options.output_format == RasterImageFormatsWithAlphaChannel.WEBP:
            save_args.update(
                {
                    "method": 4 if options.quality < 90 else 5,  # Method 4 is significantly faster than 6 with minimal quality difference
                    "lossless": options.quality >= 98,  # Only use lossless for very high quality to improve performance
                }
            )

        elif options.output_format == RasterImageFormats.TIFF:
            save_args.update({"compression": "jpeg" if image.mode == ImageConverterConstants.RGB_MODE else "tiff_deflate"})

        buffer = BytesIO()

        image.save(buffer, options.output_format, **save_args)

        return buffer.getvalue()

    @staticmethod
    def __is_large_image(image: Image.Image) -> bool:
        return image.width * image.height > ImageConverterConstants.SAFE_AREA

    @staticmethod
    def __to_rgb(rgba_image: Image.Image) -> Image.Image:
        white_color = (255, 255, 255, 255)
        white_background = Image.new(mode=ImageConverterConstants.RGBA_MODE, size=rgba_image.size, color=white_color)
        # Ensure rgba_image is in RGBA mode before compositing
        if rgba_image.mode != ImageConverterConstants.RGBA_MODE:
            rgba_image = rgba_image.convert(ImageConverterConstants.RGBA_MODE)
        # Merge RGBA into RGB with a white background
        return Image.alpha_composite(white_background, rgba_image).convert(ImageConverterConstants.RGB_MODE)
