from anydi import Module, provider

from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.auth.session_service_factory import SessionServiceFactory
from webpeditor_app.application.auth.user_service import UserService
from webpeditor_app.application.converter.commands.convert_images import ConvertImages
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.validators.conversion_request_validator import ConversionRequestValidator
from webpeditor_app.common import CloudinaryServiceABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.core import WebPEditorLoggerABC
from webpeditor_app.infrastructure import EditorQueriesABC, ConverterQueriesABC


class ApplicationModule(Module):
    @provider(scope="request")
    def conversion_request_validator_provider(
        self,
        image_file_utility: ImageFileUtilityABC,
        logger: WebPEditorLoggerABC,
    ) -> ValidatorABC[ConversionRequest]:
        return ConversionRequestValidator(image_file_utility=image_file_utility, logger=logger)

    @provider(scope="request")
    def user_service_provider(self, logger: WebPEditorLoggerABC) -> UserServiceABC:
        return UserService(logger=logger)

    @provider(scope="request")
    def convert_images_provider(
        self,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        cloudinary_service: CloudinaryServiceABC,
        image_file_utility: ImageFileUtilityABC,
        logger: WebPEditorLoggerABC,
    ) -> ConvertImages:
        return ConvertImages(
            conversion_request_validator=conversion_request_validator,
            cloudinary_service=cloudinary_service,
            image_file_utility=image_file_utility,
            logger=logger,
        )

    @provider(scope="request")
    def session_service_factory_provider(
        self,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: WebPEditorLoggerABC,
        editor_queries: EditorQueriesABC,
        converter_queries: ConverterQueriesABC,
    ) -> SessionServiceFactory:
        return SessionServiceFactory(
            user_service=user_service,
            cloudinary_service=cloudinary_service,
            logger=logger,
            editor_queries=editor_queries,
            converter_queries=converter_queries,
        )
