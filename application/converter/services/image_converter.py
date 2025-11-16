import math
from io import BytesIO
from typing import Any, Final, cast

from aiocache.backends.memory import SimpleMemoryCache
from expression import Option
from PIL import Image, ImageFile

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.converter.commands.schemas.conversion import ConversionRequest
from application.converter.services.abc.image_converter_abc import ImageConverterABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext, as_awaitable_result
from domain.converter.constants import ImageConverterConstants
from domain.converter.image_formats import RasterImageFormats, RasterImageFormatsWithAlphaChannel

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
    __CACHE: Final[SimpleMemoryCache] = SimpleMemoryCache()

    def __init__(self, image_file_utility: ImageFileServiceABC, filename_utility: FilenameServiceABC, logger: LoggerABC) -> None:
        self.__image_file_utility: Final[ImageFileServiceABC] = image_file_utility
        self.__filename_utility: Final[FilenameServiceABC] = filename_utility
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aconvert(self, file: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
        result = self.__update_filename(file, options)
        return (
            await result.bind(lambda image_file: self.__get_cache_key(image_file, options))
            .amap(self.__CACHE.get)
            .aif_then_else(
                lambda cached: cached is not None,
                ContextResult[ImageFile.ImageFile].asuccess,
                lambda _: result.abind(lambda image_file: self.__aconvert_image(image_file, options)),
            )
        )

    def __update_filename(self, image_file: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile.ImageFile]:
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
        resized_image = self.__resize_image(image_file)

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
        converted_image.filename = image_file.filename

        return (
            await self.__get_cache_key(image_file, options)
            .amap(lambda key: self.__CACHE.set(key, converted_image))
            .map(lambda _: converted_image)
        )

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

    def __get_cache_key(self, image_file: ImageFile.ImageFile, options: ConversionRequest.Options) -> ContextResult[str]:
        return self.__filename_utility.get_basename(str(image_file.filename)).map(
            lambda basename: f"{basename}_{image_file.format}->{options.output_format}_{options.quality}"
        )
