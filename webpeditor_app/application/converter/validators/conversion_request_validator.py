from typing import Final, Optional, final

from expression import Option
from ninja import UploadedFile

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

    def validate(self, value: ConversionRequest) -> ValidationResult[ConversionRequest]:
        validation_result = ValidationResult(value=value)
        files_count = len(validation_result.value.files)

        if files_count == 0:
            validation_result.add_error("No files uploaded")

        if files_count > IMAGE_CONVERTER_SETTINGS.max_total_files_count:
            validation_result.add_error("Too many files uploaded")

        for file in validation_result.value.files:
            self.__validate_filename(file.name).map(validation_result.add_error)
            self.__validate_empty_file_size(file).map(validation_result.add_error)
            self.__validate_max_file_size(file).map(validation_result.add_error)

        if validation_result.value.options.output_format.strip().upper() not in ImageConverterAllOutputFormats:
            validation_result.add_error(f"Invalid output format - {validation_result.value.options.output_format}")

        if not (
            IMAGE_CONVERTER_SETTINGS.min_quality
            <= validation_result.value.options.quality
            <= IMAGE_CONVERTER_SETTINGS.max_quality
        ):
            validation_result.add_error(
                f"Quality must be between {IMAGE_CONVERTER_SETTINGS.min_quality} and {IMAGE_CONVERTER_SETTINGS.max_quality}"
            )

        return validation_result

    def __validate_filename(self, filename: Optional[str]) -> Option[str]:
        result = self.__image_file_utility.validate_filename(filename)
        return Option[str].Some(str(result.error.message)) if result.is_error() else Option[str].Nothing()

    @staticmethod
    def __validate_empty_file_size(file: UploadedFile) -> Option[str]:
        return (
            Option[str].Some(f"Provided file {file.name} does not have size")
            if file.size is None or file.size == 0
            else Option[str].Nothing()
        )

    @staticmethod
    def __validate_max_file_size(file: UploadedFile) -> Option[str]:
        return (
            Option[str].Some(f"File {file.name} size exceeds the maximum allowed size")
            if file.size is not None and file.size > IMAGE_CONVERTER_SETTINGS.max_file_size
            else Option[str].Nothing()
        )
