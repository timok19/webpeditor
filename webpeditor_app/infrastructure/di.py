from anydi import Module, provider

from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from webpeditor_app.infrastructure.database.converter_repository import ConverterRepository
from webpeditor_app.infrastructure.database.editor_repository import EditorRepository


class InfrastructureModule(Module):
    @provider(scope="singleton")
    def provide_cloudinary_client(self, logger: LoggerABC) -> CloudinaryClient:
        return CloudinaryClient(logger)

    @provider(scope="request")
    def provide_converter_queries(self, logger: LoggerABC) -> ConverterRepositoryABC:
        return ConverterRepository(logger)

    @provider(scope="request")
    def provide_editor_queries(self) -> EditorRepositoryABC:
        return EditorRepository()
