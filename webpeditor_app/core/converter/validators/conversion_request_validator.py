from typing import Final, final

from returns.pipeline import is_successful

from webpeditor_app.common.abc.image_file_utility_service import ImageFileUtilityServiceABC
from webpeditor_app.common.validator_abc import ValidatorABC, ValidationResult
from webpeditor_app.core.converter.schemas.conversion import ConversionRequest
from webpeditor_app.core.converter.settings import IMAGE_CONVERTER_SETTINGS, ImageConverterAllOutputFormats


@final
class ConversionRequestValidator(ValidatorABC[ConversionRequest]):
    def __init__(self) -> None:
        from webpeditor_app.common.di_container import DiContainer

        self.__image_file_utility_service: Final[ImageFileUtilityServiceABC] = DiContainer.get_dependency(
            ImageFileUtilityServiceABC
        )

    def validate(self, value: ConversionRequest) -> ValidationResult:
        validation_result = ValidationResult()

        if len(value.files) == 0:
            validation_result.add_error("No files uploaded")

        if len(value.files) > IMAGE_CONVERTER_SETTINGS.max_total_files_count:
            validation_result.add_error("Too many files uploaded")

        for file in value.files:
            validate_filename_result = self.__image_file_utility_service.validate_filename(file.name)
            if not is_successful(validate_filename_result):
                validation_result.add_error(validate_filename_result.failure().message or "Invalid filename")

            if file.size is None or file.size == 0:
                validation_result.add_error(f"File {file.name} is empty")

            if file.size is not None and file.size > IMAGE_CONVERTER_SETTINGS.max_file_size:
                validation_result.add_error(f"File {file.name} size exceeds the maximum allowed size")

        if value.options.output_format.strip().upper() not in ImageConverterAllOutputFormats:
            validation_result.add_error(f"Invalid output format - {value.options.output_format}")

        if not (IMAGE_CONVERTER_SETTINGS.min_quality <= value.options.quality <= IMAGE_CONVERTER_SETTINGS.max_quality):
            validation_result.add_error(
                f"Quality must be between {IMAGE_CONVERTER_SETTINGS.min_quality} and {IMAGE_CONVERTER_SETTINGS.max_quality}"
            )

        return validation_result
