from typing import Annotated

from anydi import Module, provider
from django.http import HttpRequest
from ninja_extra.context import RouteContext

from webpeditor_app.application.common.abc.filename_utility_abc import FilenameUtilityABC
from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.common.abc.validator_abc import ValidatorABC
from webpeditor_app.application.common.session.session_service_factory import SessionServiceFactory
from webpeditor_app.application.common.session.user_service import UserService
from webpeditor_app.application.common.utilities.filename_utility import FilenameUtility
from webpeditor_app.application.common.utilities.image_file_utility import ImageFileUtility
from webpeditor_app.application.common.validators.http_request_validator import HttpRequestValidator
from webpeditor_app.application.common.validators.route_context_validator import RouteContextValidator
from webpeditor_app.application.converter.commands.convert_images_command import ConvertImagesCommand
from webpeditor_app.application.converter.commands.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.queries.get_zip_query import GetZipQuery
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.application.converter.services.image_converter import ImageConverter
from webpeditor_app.application.converter.validators.conversion_request_validator import ConversionRequestValidator
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.files_repository_abc import FilesRepositoryABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from webpeditor_app.infrastructure.files.converter.converter_files_repository import ConverterFilesRepository


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_filename_utility(self, logger: LoggerABC) -> FilenameUtilityABC:
        return FilenameUtility(logger)

    @provider(scope="request")
    def provide_image_file_utility(self, logger: LoggerABC, filename_utility: FilenameUtilityABC) -> ImageFileUtilityABC:
        return ImageFileUtility(logger, filename_utility)

    @provider(scope="singleton")
    def provide_converter_files_repository(
        self,
        logger: LoggerABC,
        cloudinary_client: CloudinaryClient,
    ) -> Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]:
        return ConverterFilesRepository(cloudinary_client, logger)

    @provider(scope="request")
    def provide_conversion_request_validator(
        self,
        image_file_utility: ImageFileUtilityABC,
        filename_utility: FilenameUtilityABC,
        logger: LoggerABC,
    ) -> ValidatorABC[ConversionRequest]:
        return ConversionRequestValidator(image_file_utility, filename_utility, logger)

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
