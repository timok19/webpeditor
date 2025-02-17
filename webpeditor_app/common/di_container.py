from typing import Any

from punq import Container, Scope

from webpeditor_app.common.abc.image_file_utility_service import ImageFileUtilityServiceABC
from webpeditor_app.common.image_file.image_file_utility_service import ImageFileUtilityService
from webpeditor_app.common.validator_abc import ValidatorABC
from webpeditor_app.core.abc.image_converter import ImageConverterABC
from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC
from webpeditor_app.core.abc.user_service import UserServiceABC
from webpeditor_app.core.auth.session_service_factory import SessionServiceFactory
from webpeditor_app.core.auth.user_service import UserService
from webpeditor_app.core.converter.image_converter import ImageConverter
from webpeditor_app.core.converter.schemas.conversion import ConversionRequest
from webpeditor_app.core.converter.validators.conversion_request_validator import ConversionRequestValidator
from webpeditor_app.core.webpeditorlogger import WebPEditorLogger
from webpeditor_app.domain.abc.converter.queries import ConverterQueriesABC
from webpeditor_app.domain.abc.editor.queries import EditorQueriesABC
from webpeditor_app.domain.converter.queries import ConverterQueries
from webpeditor_app.domain.editor.queries import EditorQueries
from webpeditor_app.infrastructure.cloudinary.cloudinary_service import CloudinaryService
from webpeditor_app.infrastructure.abc.cloudinary_service import CloudinaryServiceABC


class DiContainer:
    __di_container: Container = Container()

    @classmethod
    def create(cls) -> Container:
        # Common
        cls.__di_container.register(ImageFileUtilityServiceABC, factory=ImageFileUtilityService, scope=Scope.transient)

        # Core
        cls.__di_container.register(SessionServiceFactory, scope=Scope.transient)
        cls.__di_container.register(WebPEditorLoggerABC, factory=WebPEditorLogger, scope=Scope.singleton)
        cls.__di_container.register(UserServiceABC, factory=UserService, scope=Scope.transient)
        cls.__di_container.register(ImageConverterABC, factory=ImageConverter, scope=Scope.transient)

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
