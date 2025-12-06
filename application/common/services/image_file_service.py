from decimal import ROUND_UP, Decimal
from io import BytesIO
from typing import Final, Union, final

from PIL import ExifTags, Image, ImageFile, UnidentifiedImageError
from types_linq import Enumerable

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.services.models.file_info import ImageFileInfo
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext
from core.types import Pair

ImageFile.LOAD_TRUNCATED_IMAGES = True


@final
class ImageFileService(ImageFileServiceABC):
    __MAX_LENGTH: Final[int] = 25

    def __init__(self, logger: LoggerABC, filename_service: FilenameServiceABC) -> None:
        self.__logger: Final[LoggerABC] = logger
        self.__filename_service: Final[FilenameServiceABC] = filename_service

    def verify_integrity(self, file: ImageFile.ImageFile) -> ContextResult[ImageFile.ImageFile]:
        if file.fp is None or file.fp.closed:
            message = f"Unable to validate file integrity for '{file.filename}'. File is closed"
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.server_error(message))

        try:
            file.fp.seek(0)
            file_copy = Image.open(file.fp)
            filename_copy = file.fp.name
            file.verify()
            return self.set_filename(file_copy, filename_copy)
        except UnidentifiedImageError:
            message = f"File '{file.filename}' cannot be processed. Incompatible file type"
            self.__logger.debug(message)
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.bad_request(message))
        except Exception as exception:
            message = f"File '{file.filename}' cannot be processed. Corrupted or damaged file"
            self.__logger.exception(exception, message)
            return ContextResult[ImageFile.ImageFile].failure(ErrorContext.bad_request(message))

    def get_info(self, file: ImageFile.ImageFile) -> ContextResult[ImageFileInfo]:
        return self.__get_filename_details(file.filename).map2(self.__get_file_details(file), ImageFileInfo.create)

    def set_filename(self, file: ImageFile.ImageFile, filename: Union[str, bytes]) -> ContextResult[ImageFile.ImageFile]:
        return self.__filename_service.normalize(filename).map(lambda normalized: self.__set_filename(file, normalized))

    def __get_filename_details(self, filename: Union[str, bytes]) -> ContextResult[ImageFileInfo.FilenameDetails]:
        return (
            self.__filename_service.normalize(filename)
            .map2(self.__filename_service.get_basename(filename), Pair)
            .map2(self.__filename_service.trim(filename, self.__MAX_LENGTH), Pair)
            .map(lambda data: Enumerable(data).as_more().flatten().of_type(str).to_tuple())
            .map(lambda flatten_data: ImageFileInfo.FilenameDetails.create(*flatten_data))
        )

    def __get_file_details(self, file: ImageFile.ImageFile) -> ContextResult[ImageFileInfo.FileDetails]:
        buffer = BytesIO()

        file.save(buffer, format=file.format)

        content = buffer.getvalue()

        file_details = ImageFileInfo.FileDetails(
            format=file.format or "",
            format_description=file.format_description or "",
            content=content,
            size=len(content),
            width=file.width,
            height=file.height,
            aspect_ratio=self.__get_aspect_ratio(file.width, file.height),
            color_mode=file.mode,
            exif_data=self.__get_exif_data(file),
        )

        buffer.close()

        return ContextResult[ImageFileInfo.FileDetails].success(file_details)

    @staticmethod
    def __get_aspect_ratio(width: int, height: int) -> Decimal:
        return Decimal(width / height).quantize(Decimal(".1"), rounding=ROUND_UP)

    @staticmethod
    def __set_filename(file: ImageFile.ImageFile, filename: str) -> ImageFile.ImageFile:
        file.filename = filename
        return file

    def __get_exif_data(self, file: ImageFile.ImageFile) -> dict[str, str]:
        try:
            return {
                ExifTags.TAGS.get(tag_id, str(tag_id)): value.decode() if isinstance(value, bytes) else str(value)
                for tag_id, value in file.getexif().items()
            }
        except Exception as exception:
            self.__logger.exception(exception, "Unable to parse EXIF data")
            return {}
