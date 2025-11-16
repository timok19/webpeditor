from decimal import ROUND_UP, Decimal
from io import BytesIO
from typing import Final, Union, final

from PIL.ExifTags import TAGS
from PIL import Image, UnidentifiedImageError
from PIL.ImageFile import ImageFile

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.services.models.file_info import ImageFileInfo
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext
from core.types import Pair


@final
class ImageFileService(ImageFileServiceABC):
    __MAX_LENGTH: Final[int] = 25

    def __init__(self, logger: LoggerABC, filename_utility: FilenameServiceABC) -> None:
        self.__logger: Final[LoggerABC] = logger
        self.__filename_utility: Final[FilenameServiceABC] = filename_utility

    def get_info(self, file: ImageFile) -> ContextResult[ImageFileInfo]:
        return self.__get_filename_details(file.filename).map2(self.__get_file_details(file), ImageFileInfo.create)

    def update_filename(self, file: ImageFile, new_filename: str) -> ContextResult[ImageFile]:
        return self.__filename_utility.normalize(new_filename).map(lambda norm: self.__update_filename(file, norm))

    def verify_integrity(self, file: ImageFile) -> ContextResult[ImageFile]:
        if file.fp is None or file.fp.closed:
            message = f"Unable to validate file integrity for '{file.filename}'. File is closed"
            return ContextResult[ImageFile].failure(ErrorContext.server_error(message))

        try:
            file.fp.seek(0)
            filename_copy = file.fp.name
            file_copy = Image.open(file.fp)
            file.verify()
            return self.update_filename(file_copy, filename_copy)
        except UnidentifiedImageError:
            message = f"File '{file.filename}' cannot be processed. Incompatible file type"
            self.__logger.debug(message)
            return ContextResult[ImageFile].failure(ErrorContext.bad_request(message))
        except Exception as exception:
            message = f"File '{file.filename}' cannot be processed. Corrupted or damaged file"
            self.__logger.exception(exception, message)
            return ContextResult[ImageFile].failure(ErrorContext.bad_request(message))

    def __get_filename_details(self, filename: Union[str, bytes]) -> ContextResult[ImageFileInfo.FilenameDetails]:
        return (
            self.__filename_utility.normalize(filename)
            .bind(lambda norm: self.__filename_utility.get_basename(norm).map(lambda base: Pair[str, str](item1=norm, item2=base)))
            .bind(lambda p: self.__filename_utility.trim(p.item1, self.__MAX_LENGTH).map(lambda trimmed: (p.item1, p.item2, trimmed)))
            .map(lambda result: ImageFileInfo.FilenameDetails.create(*result))
        )

    def __get_file_details(self, file: ImageFile) -> ContextResult[ImageFileInfo.FileDetails]:
        buffer = BytesIO()

        file.save(buffer, format=file.format)

        width, height = file.size
        content = self.__get_content(buffer)
        size = self.__get_file_size(buffer)
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
            return {
                TAGS.get(tag_id, str(tag_id)): value.decode() if isinstance(value, bytes) else str(value)
                for tag_id, value in file.getexif().items()
            }
        except Exception as exception:
            self.__logger.exception(exception, "Unable to parse EXIF data")
            return {}

    @staticmethod
    def __get_content(buffer: BytesIO) -> bytes:
        return buffer.getvalue() if not buffer.closed else bytes()

    @staticmethod
    def __get_file_size(buffer: BytesIO) -> int:
        return len(buffer.getvalue()) if not buffer.closed else 0
