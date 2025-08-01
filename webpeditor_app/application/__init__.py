from typing import TYPE_CHECKING

from anydi import Module, provider

from webpeditor_app.application.common.session_service import SessionServiceFactory
from webpeditor_app.application.common.user_service import UserService, UserServiceABC
from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.common.abc.validator_abc import ValidatorABC
from webpeditor_app.application.common.cloudinary_service import CloudinaryService
from webpeditor_app.application.common.image_file.image_file_utility import ImageFileUtility
from webpeditor_app.application.converter.handlers.image_conversion_handler import ImageConversionHandler
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.application.converter.services.image_converter import ImageConverter
from webpeditor_app.application.converter.settings import ConverterSettings
from webpeditor_app.application.converter.validators.conversion_request_validator import ConversionRequestValidator
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient

if TYPE_CHECKING:
    from webpeditor_app.application.converter.handlers.schemas import ConversionRequest


class ApplicationModule(Module):
    @provider(scope="request")
    def provide_image_file_utility(self, logger: LoggerABC) -> ImageFileUtilityABC:
        return ImageFileUtility(logger=logger)

    @provider(scope="singleton")
    def provide_cloudinary_service(
        self,
        logger: LoggerABC,
        cloudinary_client: CloudinaryClient,
    ) -> CloudinaryServiceABC:
        return CloudinaryService(cloudinary_client=cloudinary_client, logger=logger)

    @provider(scope="singleton")
    def provide_converter_settings(self) -> ConverterSettings:
        return ConverterSettings()

    @provider(scope="request")
    def provide_conversion_request_validator(
        self,
        image_file_utility: ImageFileUtilityABC,
        converter_settings: ConverterSettings,
        logger: LoggerABC,
    ) -> ValidatorABC["ConversionRequest"]:
        return ConversionRequestValidator(
            image_file_utility=image_file_utility,
            converter_settings=converter_settings,
            logger=logger,
        )

    @provider(scope="request")
    def provide_user_service(self, logger: LoggerABC) -> UserServiceABC:
        return UserService(logger=logger)

    @provider(scope="request")
    def provide_session_service_factory(
        self,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: LoggerABC,
        editor_repository: EditorRepositoryABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
    ) -> SessionServiceFactory:
        return SessionServiceFactory(
            user_service=user_service,
            cloudinary_service=cloudinary_service,
            logger=logger,
            editor_repository=editor_repository,
            converter_repository=converter_repository,
            user_repository=user_repository,
        )

    @provider(scope="request")
    def provide_converter_service(self, image_file_utility: ImageFileUtilityABC) -> ImageConverterABC:
        return ImageConverter(image_file_utility=image_file_utility)

    @provider(scope="request")
    def provide_convert_images_handler(
        self,
        conversion_request_validator: ValidatorABC["ConversionRequest"],
        cloudinary_service: CloudinaryServiceABC,
        converter_service: ImageConverterABC,
        image_file_utility: ImageFileUtilityABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
        logger: LoggerABC,
    ) -> ImageConversionHandler:
        return ImageConversionHandler(
            conversion_request_validator=conversion_request_validator,
            cloudinary_service=cloudinary_service,
            converter_service=converter_service,
            image_file_utility=image_file_utility,
            converter_repo=converter_repository,
            user_repo=user_repository,
            logger=logger,
        )
