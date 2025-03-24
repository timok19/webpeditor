from typing import IO, Final, Optional, cast, final

from PIL import UnidentifiedImageError
from expression import Option
from ninja import UploadedFile
from PIL.Image import open as open_image

from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.schemas.settings import (
    IMAGE_CONVERTER_SETTINGS,
    ImageConverterAllOutputFormats,
)
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidationResult, ValidatorABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(self) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__image_file_utility: Final[ImageFileUtilityABC] = DiContainer.get_dependency(ImageFileUtilityABC)
        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)

    def validate(self, value: ConversionRequest) -> ValidationResult:
        validation_result = ValidationResult()
        files_count = len(value.files)

        if files_count == 0:
            validation_result.add_error("No files uploaded")

        if files_count > IMAGE_CONVERTER_SETTINGS.max_total_files_count:
            validation_result.add_error("Too many files uploaded")

        for file in value.files:
            self.__validate_empty_file_size(file).map(validation_result.add_error)
            self.__validate_max_file_size(file).map(validation_result.add_error)
            self.__validate_filename(file.name).map(validation_result.add_error)
            self.__validate_file_compatibility(file).map(validation_result.add_error)

        if value.options.output_format.strip().upper() not in ImageConverterAllOutputFormats:
            validation_result.add_error(f"Invalid output format '{value.options.output_format}'")

        min_quality = IMAGE_CONVERTER_SETTINGS.min_quality
        max_quality = IMAGE_CONVERTER_SETTINGS.max_quality

        if not (min_quality <= value.options.quality <= max_quality):
            validation_result.add_error(f"Quality must be between {min_quality} and {max_quality}")

        return validation_result

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        return self.__image_file_utility.validate_filename(filename).swap().map(lambda error: error.message).to_option()

    @staticmethod
    def __validate_empty_file_size(file: UploadedFile) -> Option[str]:
        return (
            Option[str].Some(f"File {file.name} does not have size")
            if file.size is None or file.size == 0
            else Option[str].Nothing()
        )

    @staticmethod
    def __validate_max_file_size(file: UploadedFile) -> Option[str]:
        max_file_size = IMAGE_CONVERTER_SETTINGS.max_file_size
        return (
            Option[str].Some(f"File {file.name} size {file.size} exceeds the maximum allowed size {max_file_size}")
            if file.size is not None and file.size > max_file_size
            else Option[str].Nothing()
        )

    def __validate_file_compatibility(self, file: UploadedFile) -> Option[str]:
        try:
            open_image(cast(IO, file.file)).verify()
            return Option[str].Nothing()
        except UnidentifiedImageError as uie:
            message = f"File '{file.name}' cannot be processed. Incompatible file"
            self.__logger.log_exception(uie, message)
            return Option[str].Some(message)
        except Exception as exc:
            message = f"File '{file.name}' cannot be processed. Corrupted or damaged file"
            self.__logger.log_exception(exc, message)
            return Option[str].Some(message)
