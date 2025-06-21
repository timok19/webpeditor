from typing import Any, Final, Optional, cast, final, Generator

from PIL import UnidentifiedImageError, Image
from expression import Option
from ninja import UploadedFile

from webpeditor_app.application.converter.schemas import ConversionRequest, ImageConverterAllOutputFormats
from webpeditor_app.application.converter.settings import ConverterSettings
from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.common.abc.validator_abc import ValidationResult, ValidatorABC
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
        self.__converter_settings: Final[ConverterSettings] = converter_settings
        self.__logger: Final[WebPEditorLoggerABC] = logger

    def validate(self, value: ConversionRequest) -> ValidationResult:
        validation_result = ValidationResult()

        for error in self.__validate(value):
            error.map(validation_result.add_error)

        return validation_result

    def __validate(self, value: ConversionRequest) -> Generator[Option[str], Any, None]:
        yield self.__validate_file_count(value.files)
        yield self.__validate_output_format(value.options.output_format)
        yield self.__validate_quality(value.options.quality)
        for file in value.files:
            yield self.__validate_empty_file_size(file)
            yield self.__validate_max_file_size(file)
            yield self.__validate_filename(file.name)
            yield self.__validate_file_compatibility(file)

    def __validate_file_count(self, files: list[UploadedFile]) -> Option[str]:
        files_count = len(files)
        if files_count == 0:
            return Option[str].Some("No files uploaded")
        if files_count > self.__converter_settings.MAX_FILES_LIMIT:
            message = f"Too many files uploaded. Allowed {self.__converter_settings.MAX_FILES_LIMIT} files to upload"
            return Option[str].Some(message)
        return Option[str].Nothing()

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        return self.__image_file_utility.normalize_filename(filename).swap().map(lambda err: err.message).to_option()

    @staticmethod
    def __validate_empty_file_size(file: UploadedFile) -> Option[str]:
        return (
            Option[str].Some(f"File {file.name} does not have size")
            if file.size is None or file.size == 0
            else Option[str].Nothing()
        )

    def __validate_max_file_size(self, file: UploadedFile) -> Option[str]:
        max_file_size = self.__converter_settings.MAX_FILE_SIZE
        if cast(int, file.size) > max_file_size:
            message = f"File {file.name} size {file.size} exceeds the maximum allowed size {max_file_size}"
            return Option[str].Some(message)
        return Option[str].Nothing()

    def __validate_file_compatibility(self, file: UploadedFile) -> Option[str]:
        try:
            Image.open(file).verify()
            return Option[str].Nothing()
        except UnidentifiedImageError as image_error:
            message = f"File '{file.name}' cannot be processed. Incompatible file"
            self.__logger.log_exception(image_error, message)
            return Option[str].Some(message)
        except Exception as exception:
            message = f"File '{file.name}' cannot be processed. Corrupted or damaged file"
            self.__logger.log_exception(exception, message)
            return Option[str].Some(message)

    @staticmethod
    def __validate_output_format(output_format: str) -> Option[str]:
        if output_format.strip().upper() not in ImageConverterAllOutputFormats:
            return Option[str].Some(f"Invalid output format '{output_format}'")
        return Option[str].Nothing()

    def __validate_quality(self, quality: int) -> Option[str]:
        if not (self.__converter_settings.MIN_QUALITY <= quality <= self.__converter_settings.MAX_QUALITY):
            message = f"Quality must be between {self.__converter_settings.MIN_QUALITY} and {self.__converter_settings.MAX_QUALITY}"
            return Option[str].Some(message)
        return Option[str].Nothing()
