from typing import Annotated

from anydi import Module, provider

from core.abc.logger_abc import LoggerABC
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from infrastructure.repositories.editor_repository import EditorRepository
from infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from infrastructure.repositories.converter_files_repository import ConverterFilesRepository
from infrastructure.repositories.converter_repository import ConverterRepository


class InfrastructureModule(Module):
    @provider(scope="singleton")
    def provide_cloudinary_client(self, logger: LoggerABC) -> CloudinaryClient:
        return CloudinaryClient(logger)

    @provider(scope="request")
    def provide_converter_repository(self, logger: LoggerABC) -> ConverterRepositoryABC:
        return ConverterRepository(logger)

    @provider(scope="singleton")
    def provide_converter_files_repository(
        self,
        logger: LoggerABC,
        cloudinary_client: CloudinaryClient,
    ) -> Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]:
        return ConverterFilesRepository(cloudinary_client, logger)

    @provider(scope="request")
    def provide_editor_repository(self) -> EditorRepositoryABC:
        return EditorRepository()
