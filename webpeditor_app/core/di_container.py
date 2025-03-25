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
from webpeditor_app.infrastructure.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.infrastructure.database.converter_queries import ConverterQueries
from webpeditor_app.infrastructure.database.editor_queries import EditorQueries
from webpeditor_app.infrastructure.cloudinary.cloudinary_service import CloudinaryService
from webpeditor_app.infrastructure.abc.cloudinary_service_abc import CloudinaryServiceABC


class DiContainer:
    __di_container: Container = Container()

    @classmethod
    def create(cls) -> Container:
        # Application
        cls.__di_container.register(ConvertImages)  # pyright: ignore [reportUnknownMemberType]

        # Validators
        cls.__di_container.register(ValidatorABC[ConversionRequest], ConversionRequestValidator)  # pyright: ignore [reportUnknownMemberType]

        # Common
        cls.__di_container.register(ImageFileUtilityABC, factory=ImageFileUtility)  # pyright: ignore [reportUnknownMemberType]

        # Core
        cls.__di_container.register(SessionServiceFactory)  # pyright: ignore [reportUnknownMemberType]
        cls.__di_container.register(WebPEditorLoggerABC, factory=WebPEditorLogger, scope=Scope.singleton)  # pyright: ignore [reportUnknownMemberType]
        cls.__di_container.register(UserServiceABC, factory=UserService)  # pyright: ignore [reportUnknownMemberType]

        # Domain
        cls.__di_container.register(EditorQueriesABC, factory=EditorQueries)  # pyright: ignore [reportUnknownMemberType]
        cls.__di_container.register(ConverterQueriesABC, factory=ConverterQueries)  # pyright: ignore [reportUnknownMemberType]

        # Infrastructure
        cls.__di_container.register(CloudinaryServiceABC, factory=CloudinaryService, scope=Scope.singleton)  # pyright: ignore [reportUnknownMemberType]

        return cls.__di_container

    @classmethod
    def get_dependency[T: object](cls, service_key: type[T], **kwargs: Any) -> T:
        """
        Get specified dependency from the DI container.
        """
        return cls.__di_container.resolve(service_key, **kwargs)  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType, reportReturnType]
