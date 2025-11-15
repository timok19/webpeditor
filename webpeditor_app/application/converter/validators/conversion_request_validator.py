from typing import Final, Optional, final, Generator, Any

from expression import Option
from ninja import UploadedFile
from types_linq import Enumerable

from webpeditor import settings
from webpeditor_app.common.abc.filename_utility_abc import FilenameUtilityABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidationResult, ValidatorABC
from webpeditor_app.application.converter.commands.schemas import ConversionRequest
from webpeditor_app.domain.converter.constants import ImageConverterConstants
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.domain.converter.image_formats import ALL_RASTER_IMAGE_FORMATS


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(self, image_file_utility: ImageFileUtilityABC, filename_utility: FilenameUtilityABC, logger: LoggerABC) -> None:
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__filename_utility: Final[FilenameUtilityABC] = filename_utility
        self.__logger: Final[LoggerABC] = logger

    def validate(self, value: ConversionRequest) -> ValidationResult:
        return ValidationResult(
            errors=Enumerable[Option[str]](self.__validate(value))
            .where(lambda result: result.is_some())
            .select(lambda result: result.some)
            .to_list()
        )

    def __validate(self, value: ConversionRequest) -> Generator[Option[str], Any, None]:
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
        if files_count > ImageConverterConstants.MAX_FILES_LIMIT:
            return Option[str].Some(f"Too many files uploaded. Allowed {ImageConverterConstants.MAX_FILES_LIMIT} files to upload")
        return Option[str].Nothing()

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        if filename is None or len(filename) == 0:
            return Option[str].Some("Filename must not be empty")

        if len(filename) > ImageConverterConstants.MAX_FILENAME_LENGTH:
            return Option[str].Some(f"Filename '{filename}' is too long (max length: {ImageConverterConstants.MAX_FILENAME_LENGTH})")

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
        message = f"File '{uploaded_file.name}' with size {uploaded_file.size} exceeds the maximum allowed size {ImageConverterConstants.MAX_FILE_SIZE}"
        return Option[str].Some(message) if uploaded_file.size > ImageConverterConstants.MAX_FILE_SIZE else Option[str].Nothing()

    @staticmethod
    def __validate_output_format(output_format: ConversionRequest.Options.OutputFormats) -> Option[str]:
        return (
            Option[str].Some(f"Invalid output format '{output_format}'")
            if output_format not in ALL_RASTER_IMAGE_FORMATS
            else Option[str].Nothing()
        )

    @staticmethod
    def __validate_quality(quality: int) -> Option[str]:
        return (
            Option[str].Some(f"Quality must be between {ImageConverterConstants.MIN_QUALITY} and {ImageConverterConstants.MAX_QUALITY}")
            if not (ImageConverterConstants.MIN_QUALITY <= quality <= ImageConverterConstants.MAX_QUALITY)
            else Option[str].Nothing()
        )
