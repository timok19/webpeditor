from anydi import Module, provider

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from webpeditor_app.infrastructure.database.converter_repository import ConverterRepository
from webpeditor_app.infrastructure.database.editor_repository import EditorRepository
from webpeditor_app.infrastructure.database.user_repository import UserRepository


class InfrastructureModule(Module):
    @provider(scope="singleton")
    def provide_cloudinary_client(self) -> CloudinaryClient:
        return CloudinaryClient()

    @provider(scope="request")
    def provide_user_queries(self, logger: WebPEditorLoggerABC) -> UserRepositoryABC:
        return UserRepository(logger=logger)

    @provider(scope="request")
    def provide_converter_queries(self, logger: WebPEditorLoggerABC) -> ConverterRepositoryABC:
        return ConverterRepository(logger=logger)

    @provider(scope="request")
    def provide_editor_queries(self) -> EditorRepositoryABC:
        return EditorRepository()
