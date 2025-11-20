from typing import Annotated

from anydi import Module, provider
from django.http import HttpRequest
from ninja_extra.context import RouteContext

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.abc.user_service_abc import UserServiceABC
from application.common.abc.validator_abc import ValidatorABC
from application.common.services.session_service_factory import SessionServiceFactory
from application.common.services.user_service import UserService
from application.common.services.filename_service import FilenameService
from application.common.services.image_file_service import ImageFileService
from application.common.validators.http_request_validator import HttpRequestValidator
from application.common.validators.route_context_validator import RouteContextValidator
from application.converter.commands.convert_images_command import ConvertImagesCommand
from application.converter.commands.schemas import ConversionRequest
from application.converter.queries.get_zip_query import GetZipQuery
from application.converter.services.abc.image_converter_abc import ImageConverterABC
from application.converter.services.image_converter import ImageConverter
from application.converter.validators.conversion_request_validator import ConversionRequestValidator
from core.abc.logger_abc import LoggerABC
from infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from infrastructure.repositories.converter_files_repository import ConverterFilesRepository


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_filename_utility(self, logger: LoggerABC) -> FilenameServiceABC:
        return FilenameService(logger)

    @provider(scope="request")
    def provide_image_file_utility(self, logger: LoggerABC, filename_utility: FilenameServiceABC) -> ImageFileServiceABC:
        return ImageFileService(logger, filename_utility)

    @provider(scope="request")
    def provide_route_context_validator(self) -> ValidatorABC[RouteContext]:
        return RouteContextValidator()

    @provider(scope="request")
    def provide_http_request_validator(self) -> ValidatorABC[HttpRequest]:
        return HttpRequestValidator()

    @provider(scope="request")
    def provide_user_service(self, logger: LoggerABC) -> UserServiceABC:
        return UserService(logger)

    @provider(scope="request")
    def provide_session_service_factory(self, user_service: UserServiceABC, logger: LoggerABC) -> SessionServiceFactory:
        return SessionServiceFactory(user_service, logger)

    @provider(scope="request")
    def provide_conversion_request_validator(
        self,
        image_file_utility: ImageFileServiceABC,
        filename_utility: FilenameServiceABC,
        logger: LoggerABC,
    ) -> ValidatorABC[ConversionRequest]:
        return ConversionRequestValidator(image_file_utility, filename_utility, logger)

    @provider(scope="request")
    def provide_converter_service(
        self,
        image_file_utility: ImageFileServiceABC,
        filename_utility: FilenameServiceABC,
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
        image_file_utility: ImageFileServiceABC,
        filename_utility: FilenameServiceABC,
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
        return GetZipQuery(
            route_context_validator,
            http_request_validator,
            session_service_factory,
            converter_files_repo,
            converter_repo,
        )
