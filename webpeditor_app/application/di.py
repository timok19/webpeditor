from typing import Annotated

from anydi import Module, provider

from webpeditor_app.application.converter.constants import ConverterConstants
from webpeditor_app.application.converter.handlers.convert_images import ConvertImages
from webpeditor_app.application.converter.handlers.get_zip import GetZip
from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.application.converter.services.image_converter import ImageConverter
from webpeditor_app.application.converter.validators.conversion_request_validator import ConversionRequestValidator
from webpeditor_app.application.editor.constants import EditorConstants
from webpeditor_app.common.abc.files_repository_abc import FilesRepositoryABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.common.image_file.image_file_utility import ImageFileUtility
from webpeditor_app.common.repositories.cloudinary_repository import CloudinaryRepository
from webpeditor_app.common.session.session_service_factory import SessionServiceFactory
from webpeditor_app.common.user.user_service import UserService
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_image_file_utility(self, logger: LoggerABC) -> ImageFileUtilityABC:
        return ImageFileUtility(logger)

    @provider(scope="singleton")
    def provide_cloudinary_repository(
        self,
        logger: LoggerABC,
        cloudinary_client: CloudinaryClient,
    ) -> Annotated[FilesRepositoryABC, CloudinaryRepository.__name__]:
        return CloudinaryRepository(cloudinary_client, logger)

    @provider(scope="singleton")
    def provide_converter_constants(self) -> ConverterConstants:
        return ConverterConstants()

    @provider(scope="singleton")
    def provide_editor_constants(self) -> EditorConstants:
        return EditorConstants()

    @provider(scope="request")
    def provide_conversion_request_validator(
        self,
        image_file_utility: ImageFileUtilityABC,
        converter_settings: ConverterConstants,
        logger: LoggerABC,
    ) -> ValidatorABC[ConversionRequest]:
        return ConversionRequestValidator(image_file_utility, converter_settings, logger)

    @provider(scope="request")
    def provide_user_service(self, logger: LoggerABC) -> UserServiceABC:
        return UserService(logger)

    @provider(scope="request")
    def provide_session_service_factory(self, user_service: UserServiceABC, logger: LoggerABC) -> SessionServiceFactory:
        return SessionServiceFactory(user_service, logger)

    @provider(scope="request")
    def provide_converter_service(self, image_file_utility: ImageFileUtilityABC, logger: LoggerABC) -> ImageConverterABC:
        return ImageConverter(image_file_utility, logger)

    @provider(scope="request")
    def provide_convert_images_handler(
        self,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        cloudinary_repo: Annotated[FilesRepositoryABC, CloudinaryRepository.__name__],
        converter_service: ImageConverterABC,
        image_file_utility: ImageFileUtilityABC,
        converter_repo: ConverterRepositoryABC,
        logger: LoggerABC,
    ) -> ConvertImages:
        return ConvertImages(
            conversion_request_validator,
            cloudinary_repo,
            converter_service,
            image_file_utility,
            converter_repo,
            logger,
        )

    @provider(scope="request")
    def provide_get_zip_handler(
        self,
        cloudinary_repo: Annotated[FilesRepositoryABC, CloudinaryRepository.__name__],
        converter_repo: ConverterRepositoryABC,
        logger: LoggerABC,
    ) -> GetZip:
        return GetZip(cloudinary_repo, converter_repo, logger)
