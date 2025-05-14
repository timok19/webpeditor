import base64
import os
import re
from decimal import ROUND_UP, Decimal
from http import HTTPStatus
from io import BytesIO
from typing import Callable, Final, Optional, Union, final

from django.core.files.base import ContentFile
from httpx import AsyncClient
from PIL.ImageFile import ImageFile
from types_linq import Enumerable

from webpeditor import settings
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import ContextResult, ErrorContext


@final
class ImageFileUtility(ImageFileUtilityABC):
    def __init__(self, logger: WebPEditorLoggerABC) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = logger
        self.__filename_regex: Final[re.Pattern[str]] = re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+")
        self.__max_filename_length: Final[int] = 25

    def to_bytes(self, file_base64: str) -> ContextResult[bytes]:
        if len(file_base64) == 0:
            return ContextResult[bytes].failure(ErrorContext.server_error("File base64 is empty"))

        base64_data = Enumerable(file_base64.split(",")).last2(None)
        if base64_data is None:
            return ContextResult[bytes].failure(ErrorContext.server_error("Invalid file base64"))

        return ContextResult[bytes].success(base64.b64decode(base64_data))

    async def aget_file_content(self, file_url: str) -> ContextResult[bytes]:
        if len(file_url) == 0:
            return ContextResult[bytes].failure(ErrorContext.server_error("File URL is empty"))

        async with AsyncClient() as client:
            file_response = await client.get(file_url)

        if file_response.status_code == HTTPStatus.NOT_FOUND.value:
            return ContextResult[bytes].failure(
                ErrorContext.not_found(f"Unable to get content of image file from url '{file_url}'")
            )

        if len(file_response.content) == 0:
            return ContextResult[bytes].failure(ErrorContext.not_found("File has no content"))

        return ContextResult[bytes].success(file_response.content)

    def get_file_info(self, image_file: ImageFile) -> ContextResult[ImageFileInfo]:
        return self.trim_filename(image_file.filename, self.__max_filename_length).bind(
            lambda trimmed_filename: self.__to_content_file(image_file).map(
                lambda content_file: ImageFileInfo(
                    content_file=content_file,
                    filename=str(content_file.name),
                    filename_shorter=trimmed_filename,
                    file_format=str(image_file.format),
                    file_format_description=image_file.format_description or "",
                    size=content_file.size,
                    width=image_file.size[0],
                    height=image_file.size[1],
                    aspect_ratio=self.__get_aspect_ratio(image_file.size),
                    color_mode=image_file.mode,
                    exif_data={},  # TODO use cloudinary to retrieve an exif data
                )
            )
        )

    def update_filename(self, image_file: ImageFile, new_filename: str) -> ContextResult[ImageFile]:
        return self.normalize_filename(new_filename).map(self.__update_filename(image_file))

    def normalize_filename(self, filename: Optional[Union[str, bytes]]) -> ContextResult[str]:
        if filename is None or len(filename) == 0:
            return ContextResult[str].failure(ErrorContext.bad_request("Filename must not be empty"))

        if isinstance(filename, bytes):
            return self.__decode_filename(filename).bind(self.normalize_filename)

        if len(filename) > settings.FILENAME_MAX_SIZE:
            message = f"Filename '{filename}' is too long (max length: {settings.FILENAME_MAX_SIZE})"
            return ContextResult[str].failure(ErrorContext.bad_request(message))

        basename, extension = os.path.splitext(filename)

        if basename.upper() in settings.RESERVED_WINDOWS_FILENAMES:
            return ContextResult[str].failure(
                ErrorContext.bad_request(f"Filename '{filename}' is a reserved name that cannot be used as a file name")
            )

        if len(extension) == 0:
            return ContextResult[str].failure(ErrorContext.bad_request(f"Filename '{filename}' has no extension"))

        return ContextResult[str].success(re.sub(self.__filename_regex, "_", filename))

    def trim_filename(self, filename: Optional[Union[str, bytes]], max_length: int) -> ContextResult[str]:
        if max_length <= 0:
            raise ValueError(f"Maximum length must be greater than 0, got {max_length}")
        return self.normalize_filename(filename).bind(self.__trim_filename(max_length))

    def __to_content_file(self, image_file: ImageFile) -> ContextResult[ContentFile[bytes]]:
        buffer = BytesIO()
        image_file.save(buffer, format=image_file.format)
        content = buffer.getvalue()
        mapped_result = self.normalize_filename(image_file.filename).map(lambda name: ContentFile(content, name))
        buffer.close()
        return mapped_result

    @staticmethod
    def __get_aspect_ratio(resolution: tuple[int, int]) -> Decimal:
        width, height = resolution
        aspect_ratio = Decimal(width / height).quantize(Decimal(".1"), rounding=ROUND_UP)
        return aspect_ratio

    def __decode_filename(self, filename: bytes) -> ContextResult[str]:
        try:
            return ContextResult[str].success(filename.decode())
        except Exception as exception:
            message = f"Invalid filename: {filename}"
            self.__logger.log_exception(exception, message)
            return ContextResult[str].failure(ErrorContext.server_error(message))

    @staticmethod
    def __update_filename(image_file: ImageFile) -> Callable[[str], ImageFile]:
        def update_filename(new_filename: str) -> ImageFile:
            image_file.filename = new_filename
            return image_file

        return update_filename

    @staticmethod
    def __trim_filename(max_length: int) -> Callable[[str], ContextResult[str]]:
        def trim_filename(filename: str) -> ContextResult[str]:
            basename, extension = os.path.splitext(filename)

            ellipsis_: Final[str] = "..."
            min_length: Final[int] = 5

            match len(filename):
                case filename_length if filename_length > max_length:
                    result = basename[: max_length - len(ellipsis_) - len(extension)] + ellipsis_ + extension
                    return ContextResult[str].success(result)
                case filename_length if min_length <= filename_length <= max_length:
                    return ContextResult[str].success(filename)
                case _:
                    message = f"Filename '{filename}' is too short. Minimal length: {min_length}"
                    return ContextResult[str].failure(ErrorContext.bad_request(message))

        return trim_filename
