import os
import re
from typing import Union, Final, final

from application.common.abc.filename_service_abc import FilenameServiceABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext
from core.types import Pair
from domain.common.constants import ImageFilePropertyConstants


@final
class FilenameService(FilenameServiceABC):
    __FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+")
    __ELLIPSIS: Final[str] = "..."

    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: LoggerABC = logger

    def normalize(self, filename: Union[str, bytes]) -> ContextResult[str]:
        return (
            self.__decode_filename(filename).bind(self.normalize)
            if isinstance(filename, bytes)
            else ContextResult[str].success(re.sub(self.__FILENAME_PATTERN, "_", filename))
        )

    def trim(self, filename: Union[str, bytes], max_length: int) -> ContextResult[str]:
        return self.normalize(filename).bind(lambda normalized: self.__trim(normalized, max_length))

    def get_basename(self, filename: Union[str, bytes]) -> ContextResult[str]:
        try:
            return (
                self.normalize(filename)
                .map(lambda normalized: Pair[str, str].from_tuple(os.path.splitext(normalized)))
                .map(lambda pair: pair.item1)
            )
        except Exception as exception:
            self.__logger.exception(exception, f"Unable to get basename from the filename '{filename}'")
            return ContextResult[str].failure(ErrorContext.server_error())

    def __decode_filename(self, filename: bytes) -> ContextResult[str]:
        try:
            return ContextResult[str].success(filename.decode())
        except Exception as exception:
            message = f"Invalid filename: {filename}"
            self.__logger.exception(exception, message)
            return ContextResult[str].failure(ErrorContext.server_error(message))

    def __trim(self, normalized_filename: str, max_length: int) -> ContextResult[str]:
        if max_length <= 0:
            raise ValueError(f"Maximum length must be greater than 0, got {max_length}")

        basename, extension = os.path.splitext(normalized_filename)

        filename_length = len(normalized_filename)

        if filename_length > max_length:
            result = basename[: max_length - len(self.__ELLIPSIS) - len(extension)] + self.__ELLIPSIS + extension
            return ContextResult[str].success(result)

        if ImageFilePropertyConstants.MIN_FILENAME_LENGTH <= filename_length <= max_length:
            return ContextResult[str].success(normalized_filename)

        message = f"Filename '{normalized_filename}' is too short. Minimal length: {ImageFilePropertyConstants.MIN_FILENAME_LENGTH}"
        return ContextResult[str].failure(ErrorContext.bad_request(message))
