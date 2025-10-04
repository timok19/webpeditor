from decimal import ROUND_UP, Decimal
from io import BytesIO
from typing import Any, Final, Union, final

from PIL.ExifTags import TAGS
from PIL import Image, UnidentifiedImageError
from PIL.ImageFile import ImageFile

from webpeditor_app.common.abc.filename_utility_abc import FilenameUtilityABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.utilities.models.file_info import ImageFileInfo
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext
from webpeditor_app.types import Pair


@final
class ImageFileUtility(ImageFileUtilityABC):
    def __init__(self, logger: LoggerABC, filename_utility: FilenameUtilityABC) -> None:
        self.__logger: Final[LoggerABC] = logger
        self.__filename_utility: Final[FilenameUtilityABC] = filename_utility
        self.__max_length: Final[int] = 25

    def get_info(self, file: ImageFile) -> ContextResult[ImageFileInfo]:
        return self.__get_filename_details(file.filename).map2(self.__get_file_details(file), ImageFileInfo.create)

    def update_filename(self, file: ImageFile, new_filename: str) -> ContextResult[ImageFile]:
        return self.__filename_utility.normalize(new_filename).map(lambda norm: self.__update_filename(file, norm))

    def close(self, file: ImageFile) -> ContextResult[None]:
        try:
            file.close()
            return ContextResult.empty_success()
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to close image file '{file}'")
            return ContextResult.empty_failure(ErrorContext.server_error())

    def validate_integrity(self, file: ImageFile) -> ContextResult[None]:
        if file.fp is None:
            message = f"Unable to validate file integrity for '{file.filename}'. File is closed"
            return ContextResult.empty_failure(ErrorContext.bad_request(message))

        try:
            Image.open(file.fp).verify()
            return ContextResult.empty_success()
        except UnidentifiedImageError:
            message = f"File '{file.filename}' cannot be processed. Incompatible file type"
            self.__logger.debug(message)
            return ContextResult.empty_failure(ErrorContext.bad_request(message))
        except Exception as exception:
            message = f"File '{file.filename}' cannot be processed. Corrupted or damaged file"
            self.__logger.exception(exception, message)
            return ContextResult.empty_failure(ErrorContext.bad_request(message))

    def __get_filename_details(self, filename: Union[str, bytes]) -> ContextResult[ImageFileInfo.FilenameDetails]:
        return (
            self.__filename_utility.normalize(filename)
            .bind(lambda norm: self.__filename_utility.get_basename(norm).map(lambda base: Pair[str, str](item1=norm, item2=base)))
            .bind(lambda p: self.__filename_utility.trim(p.item1, self.__max_length).map(lambda trimmed: (p.item1, p.item2, trimmed)))
            .map(lambda result: ImageFileInfo.FilenameDetails.create(*result))
        )

    def __get_file_details(self, file: ImageFile) -> ContextResult[ImageFileInfo.FileDetails]:
        buffer = BytesIO()

        file.save(buffer, format=file.format)

        content = buffer.getvalue()
        size = self.__get_file_size(buffer)
        width, height = file.size
        aspect_ratio = self.__get_aspect_ratio(width, height)
        exif_data = self.__get_exif_data(file)

        buffer.close()

        return ContextResult[ImageFileInfo.FileDetails].success(
            ImageFileInfo.FileDetails.create(
                file.format or "",
                file.format_description or "",
                content,
                size,
                width,
                height,
                aspect_ratio,
                file.mode,
                exif_data,
            )
        )

    @staticmethod
    def __get_aspect_ratio(width: int, height: int) -> Decimal:
        return Decimal(width / height).quantize(Decimal(".1"), rounding=ROUND_UP)

    @staticmethod
    def __update_filename(file: ImageFile, new_filename: str) -> ImageFile:
        file.filename = new_filename
        return file

    def __get_exif_data(self, file: ImageFile) -> dict[str, str]:
        try:
            return {TAGS.get(tag_id, str(tag_id)): self.__try_decode_exif_value(value) for tag_id, value in file.getexif().items()}
        except Exception as exception:
            self.__logger.exception(exception, "Unable to parse EXIF data")
            return {}

    def __try_decode_exif_value(self, value: Any) -> str:
        try:
            return value.decode() if isinstance(value, bytes) else str(value)
        except Exception:
            self.__logger.debug("Unable to decode EXIF data")
            return "<UNPROCESSABLE_BYTES>"

    @staticmethod
    def __get_file_size(buffer: BytesIO) -> int:
        return len(buffer.getvalue()) if not buffer.closed else 0
