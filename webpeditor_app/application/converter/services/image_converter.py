from io import BytesIO
import math
from typing import Any, Final, Optional, cast

from aiocache.backends.memory import SimpleMemoryCache
from expression import Option
from PIL import Image, ImageFile

from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, as_awaitable_result
from webpeditor_app.domain.converter.constants import ImageConverterConstants
from webpeditor_app.domain.converter.image_formats import RasterImageFormatsWithAlphaChannel, RasterImageFormats


class ImageConverter(ImageConverterABC):
    def __init__(self, image_file_utility: ImageFileUtilityABC, logger: LoggerABC) -> None:
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__logger: Final[LoggerABC] = logger
        self.__cache = SimpleMemoryCache()
        self.__try_enable_chunked_processing()

    @as_awaitable_result
    async def aconvert_image(self, image: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
        cached_image: Optional[ImageFile.ImageFile] = await self.__cache.get(self.__get_cache_key(image, options))
        return (
            self.__update_filename(cached_image, options)
            if cached_image is not None
            else await self.__update_filename(image, options).abind(lambda updated_image: self.__aconvert_image(updated_image, options))
        )

    def __update_filename(self, image: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
        return ContextResult[ImageFile.ImageFile].from_result(
            Option[str]
            .of_optional(image.filename)
            .to_result(ErrorContext.server_error("Image file has no filename"))
            .bind(self.__image_file_utility.normalize_filename)
            .bind(self.__image_file_utility.get_basename)
            .map(lambda basename: f"webpeditor_{basename}.{options.output_format.lower()}")
            .bind(lambda new_filename: self.__image_file_utility.update_filename(image, new_filename))
        )

    @as_awaitable_result
    async def __aconvert_image(self, image: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
        if image.format is None:
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.server_error("Unable to convert image. Invalid image format"))

        # Resize large images to improve performance
        resized_image = self.__resize_image(image)

        source_has_alpha = self.__has_alpha(resized_image)
        target_has_alpha = options.output_format in RasterImageFormatsWithAlphaChannel

        target_mode = ImageConverterConstants.RGBA_MODE if target_has_alpha else ImageConverterConstants.RGB_MODE

        # Optimize the color mode conversion
        if resized_image.mode == ImageConverterConstants.PALETTE_MODE:
            # For palette mode, convert directly to target mode
            resized_image = resized_image.convert(target_mode)
        elif source_has_alpha and not target_has_alpha:
            # Source has alpha but target doesn't, convert to RGB with white background
            resized_image = self.__to_rgb(resized_image)
        elif resized_image.mode != target_mode:
            # Convert to target mode if different
            resized_image = resized_image.convert(target_mode)

        # Save with optimized parameters for the target format
        converted_image = Image.open(self.__convert_format(resized_image, options))
        converted_image.filename = image.filename

        await self.__cache.set(self.__get_cache_key(image, options), converted_image)

        return ContextResult[ImageFile.ImageFile].success(converted_image)

    @staticmethod
    def __has_alpha(image: ImageFile.ImageFile) -> bool:
        image_format = (image.format or "").upper()
        return (image.mode == ImageConverterConstants.RGBA_MODE) or (image_format in RasterImageFormatsWithAlphaChannel)

    @staticmethod
    def __resize_image(image: ImageFile.ImageFile) -> ImageFile.ImageFile:
        width, height = image.size

        if width <= ImageConverterConstants.MAX_IMAGE_DIMENSIONS and height <= ImageConverterConstants.MAX_IMAGE_DIMENSIONS:
            return image

        # Calculate new dimensions while preserving an aspect ratio
        if width > height:
            new_width = ImageConverterConstants.MAX_IMAGE_DIMENSIONS
            new_height = math.ceil(height * (ImageConverterConstants.MAX_IMAGE_DIMENSIONS / width))
        else:
            new_height = ImageConverterConstants.MAX_IMAGE_DIMENSIONS
            new_width = math.ceil(width * (ImageConverterConstants.MAX_IMAGE_DIMENSIONS / height))

        # Use BICUBIC instead of LANCZOS for faster resizing with acceptable quality
        # BICUBIC is about 30-40% faster than LANCZOS with minimal quality difference for downsampling
        resized_image = cast(ImageFile.ImageFile, image.resize((new_width, new_height), Image.Resampling.BICUBIC))
        resized_image.format = image.format
        resized_image.filename = image.filename

        return resized_image

    @staticmethod
    def __convert_format(image: Image.Image, options: ConversionRequest.Options) -> BytesIO:
        save_args: dict[str, Any] = {"format": options.output_format, "optimize": True, "exif": image.getexif()}

        if options.output_format == RasterImageFormats.JPEG:
            width, height = image.size
            is_large_image = width * height > ImageConverterConstants.SAFE_AREA  # Only use progressive for larger images

            save_args.update(
                {
                    "quality": options.quality,
                    "subsampling": 0 if options.quality >= 95 else 2,  # Better subsampling for high quality
                    "progressive": is_large_image,  # Progressive only for large images for better performance
                }
            )

            # Ensure RGB mode for JPEG
            if image.mode != ImageConverterConstants.RGB_MODE:
                image = image.convert(ImageConverterConstants.RGB_MODE)

        elif options.output_format == RasterImageFormatsWithAlphaChannel.PNG:
            # Adjust compression level based on image size
            # Higher compression for smaller images, lower for larger ones for better performance
            width, height = image.size
            compress_level = 9 if width * height < ImageConverterConstants.SAFE_AREA else 6
            save_args.update({"compress_level": compress_level})

        elif options.output_format == RasterImageFormatsWithAlphaChannel.WEBP:
            save_args.update(
                {
                    "quality": options.quality,
                    # Use a lower method value for faster encoding with acceptable quality
                    # Method 4 is significantly faster than 6 with minimal quality difference
                    "method": 4 if options.quality < 90 else 5,
                    # Only use lossless for very high quality to improve performance
                    "lossless": options.quality >= 98,
                }
            )

        elif options.output_format == RasterImageFormats.TIFF:
            save_args.update(
                {
                    "quality": options.quality,
                    "compression": "jpeg" if image.mode == ImageConverterConstants.RGB_MODE else "tiff_deflate",
                }
            )

        buffer = BytesIO()
        image.save(buffer, **save_args)
        buffer.seek(0)

        return buffer

    @staticmethod
    def __to_rgb(rgba_image: Image.Image) -> Image.Image:
        white_color = (255, 255, 255, 255)
        white_background = Image.new(mode=ImageConverterConstants.RGBA_MODE, size=rgba_image.size, color=white_color)
        # Ensure rgba_image is in RGBA mode before compositing
        if rgba_image.mode != ImageConverterConstants.RGBA_MODE:
            rgba_image = rgba_image.convert(ImageConverterConstants.RGBA_MODE)
        # Merge RGBA into RGB with a white background
        return Image.alpha_composite(white_background, rgba_image).convert(ImageConverterConstants.RGB_MODE)

    @staticmethod
    def __try_enable_chunked_processing() -> None:
        try:
            import multiprocessing

            # Enable truncated image processing for better memory usage
            ImageFile.LOAD_TRUNCATED_IMAGES = True

            # Enable chunked processing to reduce memory usage and improve performance
            # Set PIL to use multiple cores when available
            Image.core.set_alignment(32)
            Image.core.set_blocks_max(multiprocessing.cpu_count() * 2)
            return None
        except (ImportError, AttributeError):
            return None

    @staticmethod
    def __get_cache_key(image: ImageFile.ImageFile, options: ConversionRequest.Options) -> str:
        return f"{image.format}, {options.output_format}, {options.quality}"
