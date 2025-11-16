from typing import Annotated

from anydi import Module, provider
from django.http import HttpRequest
from ninja_extra.context import RouteContext

from common.application.abc.filename_utility_abc import FilenameUtilityABC
from common.application.abc.image_file_utility_abc import ImageFileUtilityABC
from common.application.abc.validator_abc import ValidatorABC
from common.application.session.session_service_factory import SessionServiceFactory
from converter.application.commands.convert_images_command import ConvertImagesCommand
from converter.application.commands.schemas.conversion import ConversionRequest
from converter.application.queries.get_zip_query import GetZipQuery
from converter.application.services.abc.image_converter_abc import ImageConverterABC
from converter.application.services.image_converter import ImageConverter
from converter.application.validators.conversion_request_validator import ConversionRequestValidator
from common.core.abc.logger_abc import LoggerABC
from converter.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from common.infrastructure.abc.files_repository_abc import FilesRepositoryABC
from converter.infrastructure.converter_files_repository import ConverterFilesRepository


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_conversion_request_validator(
        self,
        image_file_utility: ImageFileUtilityABC,
        filename_utility: FilenameUtilityABC,
        logger: LoggerABC,
    ) -> ValidatorABC[ConversionRequest]:
        return ConversionRequestValidator(image_file_utility, filename_utility, logger)

    @provider(scope="request")
    def provide_converter_service(
        self,
        image_file_utility: ImageFileUtilityABC,
        filename_utility: FilenameUtilityABC,
        logger: LoggerABC,
    ) -> ImageConverterABC:
        return ImageConverter(image_file_utility, filename_utility, logger)

    @provider(scope="request")
    def provide_convert_images_command(
        self,
        route_context_validator: ValidatorABC[RouteContext],
        http_request_validator: ValidatorABC[HttpRequest],
        session_service_factory: SessionServiceFactory,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        image_converter: ImageConverterABC,
        image_file_utility: ImageFileUtilityABC,
        filename_utility: FilenameUtilityABC,
        converter_repo: ConverterRepositoryABC,
        logger: LoggerABC,
    ) -> ConvertImagesCommand:
        return ConvertImagesCommand(
            route_context_validator,
            http_request_validator,
            session_service_factory,
            conversion_request_validator,
            converter_files_repo,
            image_converter,
            image_file_utility,
            filename_utility,
            converter_repo,
            logger,
        )

    @provider(scope="request")
    def provide_get_zip_query(
        self,
        route_context_validator: ValidatorABC[RouteContext],
        http_request_validator: ValidatorABC[HttpRequest],
        session_service_factory: SessionServiceFactory,
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        converter_repo: ConverterRepositoryABC,
    ) -> GetZipQuery:
        return GetZipQuery(route_context_validator, http_request_validator, session_service_factory, converter_files_repo, converter_repo)
