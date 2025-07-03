from typing import Final, Optional, cast, final

from expression import Option
from ninja import UploadedFile
from PIL import Image, UnidentifiedImageError
from types_linq import Enumerable

from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.common.abc.validator_abc import ValidationResult, ValidatorABC
from webpeditor_app.application.converter.handlers.schemas import ConversionRequest, ImageConverterAllOutputFormats
from webpeditor_app.application.converter.settings import ConverterSettings
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(
        self,
        image_file_utility: ImageFileUtilityABC,
        converter_settings: ConverterSettings,
        logger: WebPEditorLoggerABC,
    ) -> None:
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__settings: Final[ConverterSettings] = converter_settings
        self.__logger: Final[WebPEditorLoggerABC] = logger

    def validate(self, value: ConversionRequest) -> ValidationResult:
        return ValidationResult(errors=self.__validate(value))

    def __validate(self, value: ConversionRequest) -> list[str]:
        results: set[Option[str]] = set[Option[str]]()
        results.add(self.__validate_file_count(value.files))
        results.add(self.__validate_output_format(value.options.output_format))
        results.add(self.__validate_quality(value.options.quality))
        for file in value.files:
            results.add(self.__validate_file_integrity(file))
            results.add(self.__validate_filename(file.name))
            results.add(self.__validate_empty_file_size(file))
            results.add(self.__validate_max_file_size(file))
        return Enumerable(results).where(lambda result: result.is_some()).select(lambda result: result.some).to_list()

    def __validate_file_count(self, files: list[UploadedFile]) -> Option[str]:
        files_count = len(files)
        if files_count == 0:
            return Option[str].Some("No files uploaded")
        if files_count > self.__settings.MAX_FILES_LIMIT:
            return Option[str].Some(f"Too many files uploaded. Allowed {self.__settings.MAX_FILES_LIMIT} files to upload")
        return Option[str].Nothing()

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        return self.__image_file_utility.normalize_filename(filename).swap().map(lambda error: error.message).to_option()

    @staticmethod
    def __validate_empty_file_size(file: UploadedFile) -> Option[str]:
        return Option[str].Some(f"File '{file.name}' does not have size") if file.size is None or file.size == 0 else Option[str].Nothing()

    def __validate_max_file_size(self, file: UploadedFile) -> Option[str]:
        return (
            Option[str].Some(f"File '{file.name}' with size {file.size} exceeds the maximum allowed size {self.__settings.MAX_FILE_SIZE}")
            if cast(int, file.size) > self.__settings.MAX_FILE_SIZE
            else Option[str].Nothing()
        )

    def __validate_file_integrity(self, file: UploadedFile) -> Option[str]:
        try:
            Image.open(file).verify()
            return Option[str].Nothing()
        except UnidentifiedImageError:
            message = f"File '{file.name}' cannot be processed. Incompatible file type '{file.content_type}'"
            self.__logger.log_debug(message)
            return Option[str].Some(message)
        except Exception as exception:
            message = f"File '{file.name}' cannot be processed. Corrupted or damaged file"
            self.__logger.log_exception(exception, message)
            return Option[str].Some(message)

    @staticmethod
    def __validate_output_format(output_format: str) -> Option[str]:
        return (
            Option[str].Some(f"Invalid output format '{output_format}'")
            if output_format.strip().upper() not in ImageConverterAllOutputFormats
            else Option[str].Nothing()
        )

    def __validate_quality(self, quality: int) -> Option[str]:
        return (
            Option[str].Some(f"Quality must be between {self.__settings.MIN_QUALITY} and {self.__settings.MAX_QUALITY}")
            if not (self.__settings.MIN_QUALITY <= quality <= self.__settings.MAX_QUALITY)
            else Option[str].Nothing()
        )
