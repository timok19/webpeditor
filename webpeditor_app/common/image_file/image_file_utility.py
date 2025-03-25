import base64
import os
import re
import exif
from decimal import ROUND_UP, Decimal
from http import HTTPStatus
from io import BytesIO
from typing import Optional, cast, final

from PIL.ImageFile import ImageFile
from django.core.files.base import ContentFile
from httpx import AsyncClient

from webpeditor import settings
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import ContextResult, ErrorContext


@final
class ImageFileUtility(ImageFileUtilityABC):
    def convert_to_bytes(self, file_base64: str) -> ContextResult[bytes]:
        if len(file_base64) == 0:
            return ContextResult[bytes].Error(ErrorContext.server_error("File base64 is empty"))

        image_base64_data: str = file_base64.split(",")[1]

        return ContextResult[bytes].Ok(base64.b64decode(image_base64_data))

    async def get_file_content_async(self, file_url: str) -> ContextResult[bytes]:
        if len(file_url) == 0:
            return ContextResult[bytes].Error(ErrorContext.server_error("File URL is empty"))

        async with AsyncClient() as client:
            file_response = await client.get(file_url)

        if file_response.status_code == HTTPStatus.NOT_FOUND.value:
            return ContextResult[bytes].Error(
                ErrorContext.not_found(f"Unable to get content of image file from url '{file_url}'")
            )

        if len(file_response.content) == 0:
            return ContextResult[bytes].Error(ErrorContext.not_found("File has no content"))

        return ContextResult[bytes].Ok(file_response.content)

    def get_file_info(self, image_file: ImageFile) -> ContextResult[ImageFileInfo]:
        content_file = self.__to_content_file(image_file)

        if content_file.size == 0:
            return ContextResult[ImageFileInfo].Error(ErrorContext.server_error("File has no content"))

        return ContextResult[ImageFileInfo].Ok(
            ImageFileInfo(
                content_file=content_file,
                filename=content_file.name,
                file_format=cast(str, image_file.format),
                file_format_description=image_file.format_description or "",
                size=content_file.size,
                resolution=image_file.size,
                aspect_ratio=self.__get_aspect_ratio(image_file.size),
                color_mode=image_file.mode,
                exif_data=self.__map_exif_data(image_file),
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
            return ContextResult[str].Error(ErrorContext.bad_request("Filename must not be empty"))

        if len(filename) > settings.FILENAME_MAX_SIZE:
            message = f"Filename '{filename}' is too long (max length: {settings.FILENAME_MAX_SIZE})"
            return ContextResult[str].Error(ErrorContext.bad_request(message))

        basename, extension = os.path.splitext(filename)

        if basename.upper() in settings.RESERVED_WINDOWS_FILENAMES:
            return ContextResult[str].Error(ErrorContext.bad_request(f"Filename '{filename}' is a reserved name"))

        if len(extension) == 0:
            return ContextResult[str].Error(ErrorContext.bad_request(f"Filename '{filename}' has no extension"))

        return ContextResult[str].Ok(filename)

    def sanitize_filename(self, filename: str) -> str:
        return re.sub(re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+"), "_", filename)

    def trim_filename(self, filename: str, *, max_length: int) -> ContextResult[str]:
        if max_length <= 0:
            return ContextResult[str].Error(
                ErrorContext.server_error(f"Maximum length must be greater than 0, got {max_length}")
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

    def __to_content_file(self, image_file: ImageFile) -> ContentFile:
        with BytesIO() as buffer:
            image_file.save(buffer, format=image_file.format)
            file_bytes = buffer.getvalue()
        return ContentFile(file_bytes, self.__get_filename(image_file))

    @staticmethod
    def __get_filename(image_file: ImageFile) -> str:
        return image_file.filename.decode() if isinstance(image_file.filename, bytes) else image_file.filename

    @staticmethod
    def __update_filename(image_file: ImageFile, new_filename: str) -> ImageFile:
        image_file.filename = new_filename
        return image_file

    @staticmethod
    def __get_aspect_ratio(resolution: tuple[int, int]) -> Decimal:
        aspect_ratio: Decimal = Decimal(resolution[0] / resolution[1])
        rounded_aspect_ratio: Decimal = aspect_ratio.quantize(Decimal(".1"), rounding=ROUND_UP)
        return rounded_aspect_ratio

    @staticmethod
    def __map_exif_data(image_file: ImageFile) -> dict[str, str]:
        image_file_copy = image_file.copy()
        with BytesIO() as buffer:
            image_file_copy.save(buffer, format=image_file.format, exif=image_file.getexif())
            image = exif.Image(buffer.getvalue())

        # Map EXIF tags to human-readable names and decode values where necessary
        exif_data = image.get_all()
        exif_map = {key: str(value) for key, value in exif_data.items()}
        return exif_map
