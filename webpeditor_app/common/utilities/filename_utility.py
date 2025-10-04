import os
import re
from typing import Union, Final, final

from webpeditor_app.common.abc.filename_utility_abc import FilenameUtilityABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext
from webpeditor_app.domain.common.constants import ImageFilePropertyConstants


@final
class FilenameUtility(FilenameUtilityABC):
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: LoggerABC = logger
        self.__filename_pattern: Final[re.Pattern[str]] = re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+")

    def normalize(self, filename: Union[str, bytes]) -> ContextResult[str]:
        return (
            self.__decode_filename(filename).bind(self.normalize)
            if isinstance(filename, bytes)
            else ContextResult[str].success(re.sub(self.__filename_pattern, "_", filename))
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

    @staticmethod
    def __trim_filename(max_length: int, filename: str) -> ContextResult[str]:
        if max_length <= 0:
            raise ValueError(f"Maximum length must be greater than 0, got {max_length}")

        basename, extension = os.path.splitext(filename)

        ellipsis_: Final[str] = "..."

        filename_length = len(filename)

        if filename_length > max_length:
            result = basename[: max_length - len(ellipsis_) - len(extension)] + ellipsis_ + extension
            return ContextResult[str].success(result)

        if ImageFilePropertyConstants.MIN_FILENAME_LENGTH <= filename_length <= max_length:
            return ContextResult[str].success(filename)

        message = f"Filename '{filename}' is too short. Minimal length: {ImageFilePropertyConstants.MIN_FILENAME_LENGTH}"
        return ContextResult[str].failure(ErrorContext.bad_request(message))
