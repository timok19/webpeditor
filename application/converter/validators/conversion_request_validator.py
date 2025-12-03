from typing import Final, Optional, final

import bitmath
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
from domain.converter.constants import ConverterConstants
from webpeditor import settings


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(self, image_file_service: ImageFileServiceABC, filename_service: FilenameServiceABC, logger: LoggerABC) -> None:
        self.__image_file_service: Final[ImageFileServiceABC] = image_file_service
        self.__filename_service: Final[FilenameServiceABC] = filename_service
        self.__logger: Final[LoggerABC] = logger

    def validate(self, value: ConversionRequest) -> ContextResult[ConversionRequest]:
        reasons = self.__validate(value)
        return (
            ContextResult[ConversionRequest].failure(ErrorContext.bad_request("Invalid request", reasons.to_list()))
            if reasons.any()
            else ContextResult[ConversionRequest].success(value)
        )

    def __validate(self, value: ConversionRequest) -> Enumerable[str]:
        return (
            self.__validate_parameters(value)
            .concat(self.__validate_files(value.files))
            .where(lambda error: error.is_some())
            .select(lambda error: error.some)
        )

    def __validate_parameters(self, value: ConversionRequest) -> Enumerable[Option[str]]:
        return (
            Enumerable[Option[str]]
            .empty()
            .append(self.__validate_file_count(value.files))
            .append(self.__validate_output_format(value.options.output_format))
            .append(self.__validate_quality(value.options.quality))
        )

    def __validate_files(self, files: list[UploadedFile]) -> Enumerable[Option[str]]:
        return (
            Enumerable[UploadedFile](files)
            .select_many(
                lambda uploaded_file: Enumerable[Option[str]]
                .empty()
                .append(self.__validate_filename(uploaded_file.name))
                .append(self.__validate_empty_file_size(uploaded_file))
                .append(self.__validate_max_file_size(uploaded_file))
            )
            .cast(Option[str])
        )

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

        basename_result = self.__filename_service.get_basename(filename)
        if basename_result.is_error():
            return basename_result.swap().map(lambda error: error.message).to_option()

        if basename_result.ok in settings.RESERVED_WINDOWS_FILENAMES:
            return Option[str].Some(f"Filename '{filename}' is a reserved name that cannot be used as a file name")

        return Option[str].Nothing()

    @staticmethod
    def __validate_empty_file_size(uploaded_file: UploadedFile) -> Option[str]:
        return Option[str].Some(f"File '{uploaded_file.name}' does not have size") if uploaded_file.size == 0 else Option[str].Nothing()

    @staticmethod
    def __validate_max_file_size(uploaded_file: UploadedFile) -> Option[str]:
        size = bitmath.Byte(uploaded_file.size or 0).to_MiB()
        max_size = bitmath.Byte(ConverterConstants.MAX_FILE_SIZE).to_MiB()
        filename = uploaded_file.name or ""
        fmt = "{value:.1f} {unit}"
        return (
            Option[str].Some(f"File '{filename}' with size {size.format(fmt)} exceeds the maximum allowed size {max_size.format(fmt)}")  # pyright: ignore
            if size > max_size
            else Option[str].Nothing()
        )

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
