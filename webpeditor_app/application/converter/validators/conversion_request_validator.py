from dataclasses import dataclass
from typing import Optional, final

from PIL import UnidentifiedImageError
from PIL.Image import open as open_image
from expression import Option
from ninja import UploadedFile

from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.schemas.output_formats import ImageConverterAllOutputFormats
from webpeditor_app.application.converter.settings import ConverterSettings
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidationResult, ValidatorABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC


@final
@dataclass
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    image_file_utility: ImageFileUtilityABC
    logger: WebPEditorLoggerABC

    def validate(self, value: ConversionRequest) -> ValidationResult:
        validation_result = ValidationResult()
        files_count = len(value.files)

        if files_count == 0:
            validation_result.add_error("No files uploaded")

        if files_count > ConverterSettings.MAX_FILES_LIMIT:
            validation_result.add_error("Too many files uploaded")

        for file in value.files:
            self.__validate_empty_file_size(file).map(validation_result.add_error)
            self.__validate_max_file_size(file).map(validation_result.add_error)
            self.__validate_filename(file.name).map(validation_result.add_error)
            self.__validate_file_compatibility(file).map(validation_result.add_error)

        if value.options.output_format.strip().upper() not in ImageConverterAllOutputFormats:
            validation_result.add_error(f"Invalid output format '{value.options.output_format}'")

        if not (ConverterSettings.MIN_QUALITY <= value.options.quality <= ConverterSettings.MAX_QUALITY):
            message = f"Quality must be between {ConverterSettings.MIN_QUALITY} and {ConverterSettings.MAX_QUALITY}"
            validation_result.add_error(message)

        return validation_result

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        return self.image_file_utility.validate_filename(filename).swap().map(lambda error: error.message).to_option()

    @staticmethod
    def __validate_empty_file_size(file: UploadedFile) -> Option[str]:
        return Option[str].Some(f"File {file.name} does not have size") if file.size == 0 else Option[str].Nothing()

    @staticmethod
    def __validate_max_file_size(file: UploadedFile) -> Option[str]:
        message = (
            f"File {file.name} size {file.size} exceeds the maximum allowed size {ConverterSettings.MAX_FILE_SIZE}"
        )
        return Option[str].Some(message) if file.size > ConverterSettings.MAX_FILE_SIZE else Option[str].Nothing()

    def __validate_file_compatibility(self, file: UploadedFile) -> Option[str]:
        try:
            open_image(file.file).verify()
            return Option[str].Nothing()
        except UnidentifiedImageError as uie:
            message = f"File '{file.name}' cannot be processed. Incompatible file"
            self.logger.log_exception(uie, message)
            return Option[str].Some(message)
        except Exception as exc:
            message = f"File '{file.name}' cannot be processed. Corrupted or damaged file"
            self.logger.log_exception(exc, message)
            return Option[str].Some(message)
