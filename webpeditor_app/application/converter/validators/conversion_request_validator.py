from typing import Final, Optional, final

from ninja import UploadedFile
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidatorABC, ValidationResult
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.schemas.settings import (
    IMAGE_CONVERTER_SETTINGS,
    ImageConverterAllOutputFormats,
)


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(self) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__image_file_utility: Final[ImageFileUtilityABC] = DiContainer.get_dependency(ImageFileUtilityABC)

    def validate(self, value: ConversionRequest) -> ValidationResult:
        validation_result = ValidationResult()
        files_count = len(value.files)

        if files_count == 0:
            validation_result.add_error("No files uploaded")

        if files_count > IMAGE_CONVERTER_SETTINGS.max_total_files_count:
            validation_result.add_error("Too many files uploaded")

        for file in value.files:
            self.__validate_filename(file.name).alt(validation_result.add_error)
            self.__validate_empty_file_size(file).alt(validation_result.add_error)
            self.__validate_max_file_size(file).alt(validation_result.add_error)

        if value.options.output_format.strip().upper() not in ImageConverterAllOutputFormats:
            validation_result.add_error(f"Invalid output format - {value.options.output_format}")

        if not (IMAGE_CONVERTER_SETTINGS.min_quality <= value.options.quality <= IMAGE_CONVERTER_SETTINGS.max_quality):
            validation_result.add_error(
                f"Quality must be between {IMAGE_CONVERTER_SETTINGS.min_quality} and {IMAGE_CONVERTER_SETTINGS.max_quality}"
            )

        return validation_result

    def __validate_filename(self, filename: Optional[str]) -> Result[None, str]:
        return (
            Failure(result.failure().message or "Invalid filename")
            if not is_successful(result := self.__image_file_utility.validate_filename(filename))
            else Success(None)
        )

    @staticmethod
    def __validate_empty_file_size(file: UploadedFile) -> Result[None, str]:
        return (
            Failure(f"Provided file {file.name} does not have size")
            if file.size is None or file.size == 0
            else Success(None)
        )

    @staticmethod
    def __validate_max_file_size(file: UploadedFile) -> Result[None, str]:
        return (
            Failure(f"File {file.name} size exceeds the maximum allowed size")
            if file.size is not None and file.size > IMAGE_CONVERTER_SETTINGS.max_file_size
            else Success(None)
        )
