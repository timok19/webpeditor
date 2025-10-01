import base64
import os
import re
from decimal import ROUND_UP, Decimal
from http import HTTPStatus
from io import BytesIO
from typing import Callable, Final, Union, final

import exifread
from httpx import AsyncClient
from PIL.ImageFile import ImageFile
from types_linq import Enumerable

from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.models import ImageFileInfo
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext
from webpeditor_app.types import Pair, Unit


@final
class ImageFileUtility(ImageFileUtilityABC):
    __filename_pattern: Final[re.Pattern[str]] = re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+")
    __max_length: Final[int] = 25

    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

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
            return ContextResult[bytes].failure(ErrorContext.not_found(f"Unable to get content of image file from url '{file_url}'"))

        if len(file_response.content) == 0:
            return ContextResult[bytes].failure(ErrorContext.not_found("File has no content"))

        return ContextResult[bytes].success(file_response.content)

    def get_file_info(self, image: ImageFile) -> ContextResult[ImageFileInfo]:
        return self.__get_filename_details(image.filename).map2(self.__get_file_details(image), ImageFileInfo.create)

    def update_filename(self, image: ImageFile, new_filename: str) -> ContextResult[ImageFile]:
        return self.normalize_filename(new_filename).map(self.__update_filename(image))

    def normalize_filename(self, filename: Union[str, bytes]) -> ContextResult[str]:
        return (
            self.__decode_filename(filename).bind(self.normalize_filename)
            if isinstance(filename, bytes)
            else ContextResult[str].success(re.sub(self.__filename_pattern, "_", filename))
        )

    def trim_filename(self, filename: Union[str, bytes], max_length: int) -> ContextResult[str]:
        return self.normalize_filename(filename).bind(lambda normalized: self.__trim_filename(max_length, normalized))

    def get_basename(self, filename: str) -> ContextResult[str]:
        try:
            basename, _ = os.path.splitext(filename)
            return ContextResult[str].success(basename)
        except Exception as exception:
            self.__logger.exception(exception, f"Unable to get basename from the filename '{filename}'")
            return ContextResult[str].failure(ErrorContext.server_error())

    def close_image(self, image: ImageFile) -> ContextResult[Unit]:
        try:
            image.close()
            return ContextResult[Unit].success(Unit())
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to close image file '{image}'")
            return ContextResult[Unit].failure(ErrorContext.server_error())

    def __get_filename_details(self, filename: Union[str, bytes]) -> ContextResult[ImageFileInfo.FilenameDetails]:
        return (
            self.normalize_filename(filename)
            .bind(lambda normalized: self.get_basename(normalized).map(lambda basename: Pair[str, str](item1=normalized, item2=basename)))
            .bind(lambda pair: self.trim_filename(pair.item1, self.__max_length).map(lambda trimmed: (pair.item1, pair.item2, trimmed)))
            .map(lambda result: ImageFileInfo.FilenameDetails.create(*result))
        )

    def __get_file_details(self, image: ImageFile) -> ContextResult[ImageFileInfo.FileDetails]:
        buffer = BytesIO()

        image.save(buffer, format=image.format)

        content = buffer.getvalue()
        size = self.__get_file_size(buffer)
        width, height = image.size
        aspect_ratio = self.__get_aspect_ratio(width, height)
        exif_data = self.__get_exif_data(buffer)

        buffer.close()

        return ContextResult[ImageFileInfo.FileDetails].success(
            ImageFileInfo.FileDetails.create(
                image.format or "",
                image.format_description or "",
                content,
                size,
                width,
                height,
                aspect_ratio,
                image.mode,
                exif_data,
            )
        )

    @staticmethod
    def __get_aspect_ratio(width: int, height: int) -> Decimal:
        return Decimal(width / height).quantize(Decimal(".1"), rounding=ROUND_UP)

    def __decode_filename(self, filename: bytes) -> ContextResult[str]:
        try:
            return ContextResult[str].success(filename.decode())
        except Exception as exception:
            message = f"Invalid filename: {filename}"
            self.__logger.exception(exception, message)
            return ContextResult[str].failure(ErrorContext.server_error(message))

    @staticmethod
    def __update_filename(image: ImageFile) -> Callable[[str], ImageFile]:
        def update_filename(new_filename: str) -> ImageFile:
            image.filename = new_filename
            return image

        return update_filename

    @staticmethod
    def __trim_filename(max_length: int, filename: str) -> ContextResult[str]:
        if max_length <= 0:
            raise ValueError(f"Maximum length must be greater than 0, got {max_length}")

        basename, extension = os.path.splitext(filename)

        ellipsis_: Final[str] = "..."
        min_length: Final[int] = 5

        filename_length = len(filename)

        if filename_length > max_length:
            result = basename[: max_length - len(ellipsis_) - len(extension)] + ellipsis_ + extension
            return ContextResult[str].success(result)

        if min_length <= filename_length <= max_length:
            return ContextResult[str].success(filename)

        message = f"Filename '{filename}' is too short. Minimal length: {min_length}"
        return ContextResult[str].failure(ErrorContext.bad_request(message))

    def __get_exif_data(self, buffer: BytesIO) -> dict[str, str]:
        if buffer.closed:
            return {}

        try:
            exif_image = exifread.process_file(buffer, debug=True)
            return {k: str(v) for k, v in exif_image.items()}
        except Exception as exception:
            self.__logger.exception(exception, "Unable to parse EXIF data")
            return {}

    @staticmethod
    def __get_file_size(buffer: BytesIO) -> int:
        return len(buffer.getvalue()) if not buffer.closed else 0
