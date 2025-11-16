import os
import re
from typing import Union, Final, final

from common.application.abc.filename_utility_abc import FilenameUtilityABC
from common.core.abc.logger_abc import LoggerABC
from common.core.result import ContextResult, ErrorContext
from common.domain.constants import ImageFilePropertyConstants


@final
class FilenameUtility(FilenameUtilityABC):
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
        return self.normalize(filename).bind(lambda normalized: self.__trim_filename(max_length, normalized))

    def get_basename(self, filename: str) -> ContextResult[str]:
        try:
            basename, _ = os.path.splitext(filename)
            return ContextResult[str].success(basename)
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

    def __trim_filename(self, max_length: int, filename: str) -> ContextResult[str]:
        if max_length <= 0:
            raise ValueError(f"Maximum length must be greater than 0, got {max_length}")

        basename, extension = os.path.splitext(filename)

        filename_length = len(filename)

        if filename_length > max_length:
            result = basename[: max_length - len(self.__ELLIPSIS) - len(extension)] + self.__ELLIPSIS + extension
            return ContextResult[str].success(result)

        if ImageFilePropertyConstants.MIN_FILENAME_LENGTH <= filename_length <= max_length:
            return ContextResult[str].success(filename)

        message = f"Filename '{filename}' is too short. Minimal length: {ImageFilePropertyConstants.MIN_FILENAME_LENGTH}"
        return ContextResult[str].failure(ErrorContext.bad_request(message))
