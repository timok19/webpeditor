from typing import Any

from punq import Container, Scope

from webpeditor_app.application.converter.commands.convert_images import ConvertImages
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.application.converter.validators.conversion_request_validator import ConversionRequestValidator
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.image_file_utility import ImageFileUtility
from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.application.auth.session_service_factory import SessionServiceFactory
from webpeditor_app.application.auth.user_service import UserService
from webpeditor_app.core.webpeditor_logger import WebPEditorLogger
from webpeditor_app.infrastructure.database.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.database.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.infrastructure.database.converter_queries import ConverterQueries
from webpeditor_app.infrastructure.database.editor_queries import EditorQueries
from webpeditor_app.infrastructure.cloudinary.cloudinary_service import CloudinaryService
from webpeditor_app.infrastructure.abc.cloudinary_service_abc import CloudinaryServiceABC


class DiContainer:
    __di_container: Container = Container()

    @classmethod
    def create(cls) -> Container:
        # Common
        cls.__di_container.register(ImageFileUtilityABC, factory=ImageFileUtility, scope=Scope.transient)

        # Core
        cls.__di_container.register(SessionServiceFactory, scope=Scope.transient)
        cls.__di_container.register(WebPEditorLoggerABC, factory=WebPEditorLogger, scope=Scope.singleton)
        cls.__di_container.register(UserServiceABC, factory=UserService, scope=Scope.transient)
        cls.__di_container.register(ConvertImages, scope=Scope.transient)

        # Domain
        cls.__di_container.register(EditorQueriesABC, factory=EditorQueries, scope=Scope.transient)
        cls.__di_container.register(ConverterQueriesABC, factory=ConverterQueries, scope=Scope.transient)

        # Validators
        cls.__di_container.register(ValidatorABC[ConversionRequest], ConversionRequestValidator, scope=Scope.transient)

        # Infrastructure
        cls.__di_container.register(CloudinaryServiceABC, factory=CloudinaryService, scope=Scope.singleton)

        return cls.__di_container

    @classmethod
    def get_dependency[T: object](cls, service_key: type[T], **kwargs: Any) -> T:
        """
        Get specified dependency from the DI container.
        """
        return cls.__di_container.resolve(service_key, **kwargs)
