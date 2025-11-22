from typing import Any, Final, Generator, Optional, cast, final

from expression import Option
from ninja import UploadedFile
from types_linq import Enumerable

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.abc.validator_abc import ValidatorABC
from application.converter.commands.schemas import ConversionRequest
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult
from core.result.error_context import ErrorContext
from domain.constants.converter_constants import ConverterConstants
from webpeditor import settings


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(self, image_file_utility: ImageFileServiceABC, filename_utility: FilenameServiceABC, logger: LoggerABC) -> None:
        self.__image_file_utility: Final[ImageFileServiceABC] = image_file_utility
        self.__filename_utility: Final[FilenameServiceABC] = filename_utility
        self.__logger: Final[LoggerABC] = logger

    def validate(self, value: Optional[ConversionRequest]) -> ContextResult[ConversionRequest]:
        reasons = Enumerable(self.__validate(value)).where(lambda error: error.is_some()).select(lambda error: error.some)
        return (
            ContextResult[ConversionRequest].failure(ErrorContext.bad_request("Invalid request", reasons.to_list()))
            if reasons.any()
            else ContextResult[ConversionRequest].success(cast(ConversionRequest, value))
        )

    def __validate(self, value: Optional[ConversionRequest]) -> Generator[Option[str], Any, None]:
        if value is None:
            yield Option[str].Some(f"{ConversionRequest.__name__} is empty")
            return
        yield self.__validate_file_count(value.files)
        yield self.__validate_output_format(value.options.output_format)
        yield self.__validate_quality(value.options.quality)
        for uploaded_file in value.files:
            yield self.__validate_filename(uploaded_file.name)
            yield self.__validate_empty_file_size(uploaded_file)
            yield self.__validate_max_file_size(uploaded_file)

    @staticmethod
    def __validate_file_count(files: list[UploadedFile]) -> Option[str]:
        files_count = len(files)
        if files_count == 0:
            return Option[str].Some("No files uploaded")
        if files_count > ConverterConstants.MAX_FILES_LIMIT:
            return Option[str].Some(f"Too many files uploaded. Allowed {ConverterConstants.MAX_FILES_LIMIT} files to upload")
        return Option[str].Nothing()

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        if filename is None or len(filename) == 0:
            return Option[str].Some("Filename must not be empty")

        if len(filename) > ConverterConstants.MAX_FILENAME_LENGTH:
            return Option[str].Some(f"Filename '{filename}' is too long (max length: {ConverterConstants.MAX_FILENAME_LENGTH})")

        if (basename_result := self.__filename_utility.get_basename(filename)).is_error():
            return basename_result.swap().map(lambda error: error.message).to_option()

        if basename_result.ok in settings.RESERVED_WINDOWS_FILENAMES:
            return Option[str].Some(f"Filename '{filename}' is a reserved name that cannot be used as a file name")

        return Option[str].Nothing()

    @staticmethod
    def __validate_empty_file_size(uploaded_file: UploadedFile) -> Option[str]:
        return Option[str].Some(f"File '{uploaded_file.name}' does not have size") if uploaded_file.size == 0 else Option[str].Nothing()

    @staticmethod
    def __validate_max_file_size(uploaded_file: UploadedFile) -> Option[str]:
        message = f"File '{uploaded_file.name}' with size {uploaded_file.size} exceeds the maximum allowed size {ConverterConstants.MAX_FILE_SIZE}"
        return Option[str].Some(message) if uploaded_file.size > ConverterConstants.MAX_FILE_SIZE else Option[str].Nothing()

    @staticmethod
    def __validate_output_format(output_format: ConversionRequest.Options.OutputFormats) -> Option[str]:
        return (
            Option[str].Some(f"Invalid output format '{output_format}'")
            if output_format not in ConverterConstants.ALL_IMAGE_FORMATS
            else Option[str].Nothing()
        )

    @staticmethod
    def __validate_quality(quality: int) -> Option[str]:
        return (
            Option[str].Some(f"Quality must be between {ConverterConstants.MIN_QUALITY} and {ConverterConstants.MAX_QUALITY}")
            if not (ConverterConstants.MIN_QUALITY <= quality <= ConverterConstants.MAX_QUALITY)
            else Option[str].Nothing()
        )
