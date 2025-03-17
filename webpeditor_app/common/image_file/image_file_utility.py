import base64
import os
import re
from decimal import ROUND_UP, Decimal
from fractions import Fraction
from http import HTTPStatus
from io import BytesIO
from typing import Optional, final

from PIL.ImageFile import ImageFile
from django.core.files.base import ContentFile
from httpx import AsyncClient
from PIL.ExifTags import TAGS
from PIL.Image import Exif
from PIL.TiffImagePlugin import IFDRational

from webpeditor import settings
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import ContextResult, ErrorContext


@final
class ImageFileUtility(ImageFileUtilityABC):
    def convert_to_bytes(self, file_base64: str) -> ContextResult[bytes]:
        if len(file_base64) == 0:
            return ContextResult[bytes].Error2(ErrorContext.ErrorCode.INTERNAL_SERVER_ERROR, "File base64 is empty")

        image_base64_data: str = file_base64.split(",")[1]

        return ContextResult[bytes].Ok(base64.b64decode(image_base64_data))

    async def get_file_content_async(self, file_url: str) -> ContextResult[bytes]:
        if len(file_url) == 0:
            return ContextResult[bytes].Error2(ErrorContext.ErrorCode.INTERNAL_SERVER_ERROR, "File URL is empty")

        async with AsyncClient() as client:
            file_response = await client.get(file_url)

        if file_response.status_code == HTTPStatus.NOT_FOUND.value:
            return ContextResult[bytes].Error2(
                ErrorContext.ErrorCode.NOT_FOUND, f"Unable to get content of image file from url '{file_url}'"
            )

        if len(file_response.content) == 0 or file_response.content is None:
            return ContextResult[bytes].Error2(ErrorContext.ErrorCode.NOT_FOUND, "File has no content")

        return ContextResult[bytes].Ok(file_response.content)

    def get_file_info(self, image_file: ImageFile) -> ContextResult[ImageFileInfo]:
        with BytesIO() as buffer:
            image_file.save(buffer, format=image_file.format)
            image_file_bytes = buffer.getvalue()

        if len(image_file_bytes) == 0:
            return ContextResult[ImageFileInfo].Error2(
                ErrorContext.ErrorCode.INTERNAL_SERVER_ERROR, "File has no content"
            )

        filename = image_file.filename.decode() if isinstance(image_file.filename, bytes) else image_file.filename
        content_file = ContentFile(image_file_bytes, filename)

        if image_file.format is None:
            return ContextResult[ImageFileInfo].Error2(
                ErrorContext.ErrorCode.INTERNAL_SERVER_ERROR,
                "Failed to read image file format",
            )

        file_format_description = image_file.format_description or ""
        resolution = image_file.size
        aspect_ratio = self.__get_aspect_ratio(resolution)
        color_mode = image_file.mode
        mapped_exif_data = self.__map_exif_data(image_file.getexif())

        return ContextResult[ImageFileInfo].Ok(
            ImageFileInfo(
                content_file=content_file,
                filename=filename,
                file_format=image_file.format,
                file_format_description=file_format_description,
                size=content_file.size,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                color_mode=color_mode,
                exif_data=mapped_exif_data,
            )
        )

    def update_filename(self, image_file: ImageFile, new_filename: str) -> ContextResult[ImageFile]:
        return (
            self.validate_filename(new_filename)
            .map(self.sanitize_filename)
            .map(lambda sanitized_filename: self.__update_filename(image_file, sanitized_filename))
        )

    def validate_filename(self, filename: Optional[str]) -> ContextResult[str]:
        if filename is None or len(filename) == 0:
            return ContextResult[str].Error2(ErrorContext.ErrorCode.BAD_REQUEST, "Filename must not be empty")

        if len(filename) > settings.FILENAME_MAX_SIZE:
            return ContextResult[str].Error2(
                ErrorContext.ErrorCode.BAD_REQUEST,
                f"Filename '{filename}' is too long (max length: {settings.FILENAME_MAX_SIZE})",
            )

        basename, extension = os.path.splitext(filename)

        if basename.upper() in settings.RESERVED_WINDOWS_FILENAMES:
            return ContextResult[str].Error2(
                ErrorContext.ErrorCode.BAD_REQUEST,
                f"Filename '{filename}' is a reserved name",
            )

        if len(extension) == 0:
            return ContextResult[str].Error2(
                ErrorContext.ErrorCode.BAD_REQUEST,
                f"Filename '{filename}' has no extension",
            )

        return ContextResult[str].Ok(filename)

    def sanitize_filename(self, filename: str) -> str:
        return re.sub(re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+"), "_", filename)

    def trim_filename(self, filename: str, *, max_length: int) -> ContextResult[str]:
        if max_length <= 0:
            return ContextResult[str].Error2(
                ErrorContext.ErrorCode.INTERNAL_SERVER_ERROR,
                f"Maximum length must be greater than 0, got {max_length}",
            )

        if len(filename) <= max_length:
            return ContextResult[str].Ok(filename)

        basename, extension = os.path.splitext(filename)

        ellipsis_str: str = "..."
        ellipsis_len: int = len(ellipsis_str)

        # Minimum space needed: 3 for ellipsis + length of extension
        min_required_length: int = len(extension) + ellipsis_len

        if max_length < min_required_length:
            return ContextResult[str].Ok(f"{basename[: max_length - ellipsis_len]}{ellipsis_str}")

        return ContextResult[str].Ok(f"{basename[: (max_length - min_required_length)]}{ellipsis_str}{extension}")

    @staticmethod
    def __update_filename(image_file: ImageFile, new_filename: str) -> ImageFile:
        image_file.filename = new_filename
        return image_file

    @staticmethod
    def __get_aspect_ratio(resolution: tuple[int, int]) -> Decimal:
        aspect_ratio: Decimal = Decimal(resolution[0] / resolution[1])
        rounded_aspect_ratio: Decimal = aspect_ratio.quantize(Decimal(".1"), rounding=ROUND_UP)
        return rounded_aspect_ratio

    def __map_exif_data(self, exif: Exif) -> dict[str, str]:
        # If no EXIF data is found, return an empty dictionary
        if not exif or len(exif) == 0:
            return {}

        exif_map: dict[str, str] = {}

        # Map EXIF tags to human-readable names and decode values where necessary
        for tag_id in exif:
            if len(decoded_exif := self.__decode_exif_value(exif[tag_id])) > 0:
                exif_map[TAGS[tag_id]] = decoded_exif

        return exif_map

    @staticmethod
    def __decode_exif_value(value: object) -> str:
        if isinstance(value, bytes):
            return value.decode()
        elif isinstance(value, IFDRational):
            return str(float(Fraction(int(value.numerator), int(value.denominator))))
        else:
            return str(value)
