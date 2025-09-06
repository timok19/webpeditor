from io import BytesIO
from typing import Any, ClassVar, Final, cast

from expression import Option
from PIL import Image, ImageFile

from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.converter.handlers.schemas import (
    ImageConverterAllOutputFormats,
    ImageConverterOutputFormatsWithAlphaChannel,
)
from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.application.converter.constants import ConverterConstants
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result.context_result import ContextResult, ErrorContext


class ImageConverter(ImageConverterABC):
    __rgb_mode: ClassVar[str] = "RGB"
    __rgba_mode: ClassVar[str] = "RGBA"
    __palette_mode: ClassVar[str] = "P"

    def __init__(self, image_file_utility: ImageFileUtilityABC, logger: LoggerABC) -> None:
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__logger: Final[LoggerABC] = logger
        self.__cache_request: dict[tuple[str, ImageConverterAllOutputFormats, int], ImageFile.ImageFile] = {}
        self.__try_enable_chunked_processing()

    def convert_image(
        self,
        image: ImageFile.ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile.ImageFile]:
        cached_image = self.__cache_request.get((str(image.format), options.output_format, options.quality))
        return (
            self.__update_filename(cached_image, options)
            if cached_image is not None
            else self.__update_filename(image, options).bind(lambda updated_image: self.__convert_image(updated_image, options))
        )

    def __update_filename(
        self,
        image_file: ImageFile.ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile.ImageFile]:
        return ContextResult[ImageFile.ImageFile].from_result(
            Option[str]
            .of_optional(image_file.filename)
            .to_result(ErrorContext.server_error("Image file has no filename"))
            .bind(self.__image_file_utility.normalize_filename)
            .bind(self.__image_file_utility.get_basename)
            .map(lambda basename: f"webpeditor_{basename}.{options.output_format.lower()}")
            .bind(lambda new_filename: self.__image_file_utility.update_filename(image_file, new_filename))
        )

    def __convert_image(
        self,
        image: ImageFile.ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile.ImageFile]:
        if image.format is None:
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.server_error("Unable to convert image. Invalid image format"))

        # Resize large images to improve performance
        img = self.__limit_image_size(image)

        source_has_alpha = (img.mode == self.__rgba_mode) or (str(img.format).upper() in ImageConverterOutputFormatsWithAlphaChannel)
        target_has_alpha = options.output_format in ImageConverterOutputFormatsWithAlphaChannel

        target_mode = self.__rgba_mode if target_has_alpha else self.__rgb_mode

        # Optimize the color mode conversion
        if img.mode == self.__palette_mode:
            # For palette mode, convert directly to target mode
            img = img.convert(target_mode)
        elif source_has_alpha and not target_has_alpha:
            # Source has alpha but target doesn't, convert to RGB with white background
            img = self.__to_rgb(img)
        elif img.mode != target_mode:
            # Convert to target mode if different
            img = img.convert(target_mode)

        # Save with optimized parameters for the target format
        result = Image.open(self.__convert_format(img, options))
        result.filename = image.filename

        self.__cache_request.setdefault((str(image.format), options.output_format, options.quality), result)

        return ContextResult[ImageFile.ImageFile].success(result)

    @staticmethod
    def __limit_image_size(image: ImageFile.ImageFile) -> ImageFile.ImageFile:
        width, height = image.size

        if width <= ConverterConstants.MAX_IMAGE_DIMENSIONS and height <= ConverterConstants.MAX_IMAGE_DIMENSIONS:
            return image

        # Calculate new dimensions while preserving an aspect ratio
        if width > height:
            new_width = ConverterConstants.MAX_IMAGE_DIMENSIONS
            new_height = int(height * (ConverterConstants.MAX_IMAGE_DIMENSIONS / width))
        else:
            new_height = ConverterConstants.MAX_IMAGE_DIMENSIONS
            new_width = int(width * (ConverterConstants.MAX_IMAGE_DIMENSIONS / height))

        # Use BICUBIC instead of LANCZOS for faster resizing with acceptable quality
        # BICUBIC is about 30-40% faster than LANCZOS with minimal quality difference for downsampling
        resized_img = cast(ImageFile.ImageFile, image.resize((new_width, new_height), Image.Resampling.BICUBIC))
        resized_img.format = image.format
        resized_img.filename = image.filename

        return resized_img

    def __convert_format(self, image: Image.Image, options: ConversionRequest.Options) -> BytesIO:
        save_args: dict[str, Any] = {"format": options.output_format, "optimize": True, "exif": image.getexif()}

        if options.output_format == ImageConverterAllOutputFormats.JPEG:
            width, height = image.size
            is_large_image = width * height > ConverterConstants.SAFE_AREA  # Only use progressive for larger images

            save_args.update(
                {
                    "quality": options.quality,
                    "subsampling": 0 if options.quality >= 95 else 2,  # Better subsampling for high quality
                    "progressive": is_large_image,  # Progressive only for large images for better performance
                }
            )

            # Ensure RGB mode for JPEG
            if image.mode != self.__rgb_mode:
                image = image.convert(self.__rgb_mode)

        elif options.output_format == ImageConverterAllOutputFormats.PNG:
            # Adjust compression level based on image size
            # Higher compression for smaller images, lower for larger ones for better performance
            width, height = image.size
            compress_level = 9 if width * height < ConverterConstants.SAFE_AREA else 6
            save_args.update({"compress_level": compress_level})

        elif options.output_format == ImageConverterAllOutputFormats.WEBP:
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

        elif options.output_format == ImageConverterAllOutputFormats.TIFF:
            save_args.update({"quality": options.quality, "compression": "jpeg" if image.mode == self.__rgb_mode else "tiff_deflate"})

        buffer = BytesIO()
        image.save(buffer, **save_args)
        buffer.seek(0)

        return buffer

    def __to_rgb(self, rgba_image: Image.Image) -> Image.Image:
        white_color = (255, 255, 255, 255)
        white_background = Image.new(mode=self.__rgba_mode, size=rgba_image.size, color=white_color)
        # Ensure rgba_image is in RGBA mode before compositing
        if rgba_image.mode != self.__rgba_mode:
            rgba_image = rgba_image.convert(self.__rgba_mode)
        # Merge RGBA into RGB with a white background
        return Image.alpha_composite(white_background, rgba_image).convert(self.__rgb_mode)

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
