from typing import Annotated

from anydi import Module, provider

from core.abc.logger_abc import LoggerABC
from infrastructure.abc.converter_image_assets_repository_abc import ConverterImageAssetsRepositoryABC
from infrastructure.abc.editor_image_assets_repository_abc import EditorImageAssetsRepositoryABC
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from infrastructure.repositories.converter_files.converter_files_repository import ConverterFilesRepository
from infrastructure.repositories.converter_image_assets.converter_image_assets_repository import ConverterImageAssetsRepository
from infrastructure.repositories.editor_image_assets.editor_image_assets_repository import EditorImageAssetsRepository


class InfrastructureModule(Module):
    @provider(scope="singleton")
    def provide_cloudinary_client(self, logger: LoggerABC) -> CloudinaryClient:
        return CloudinaryClient(logger)

    @provider(scope="request")
    def provide_converter_image_assets_repository(self, logger: LoggerABC) -> ConverterImageAssetsRepositoryABC:
        return ConverterImageAssetsRepository(logger)

    @provider(scope="singleton")
    def provide_converter_files_repository(
        self,
        logger: LoggerABC,
        cloudinary_client: CloudinaryClient,
    ) -> Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]:
        return ConverterFilesRepository(cloudinary_client, logger)

    @provider(scope="request")
    def provide_editor_image_assets_repository(self) -> EditorImageAssetsRepositoryABC:
        return EditorImageAssetsRepository()
