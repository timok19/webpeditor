from typing import Annotated

from anydi import Module, provider

from common.infrastructure.abc.files_repository_abc import FilesRepositoryABC
from common.infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from converter.infrastructure.converter_files_repository import ConverterFilesRepository
from common.core.abc.logger_abc import LoggerABC
from converter.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from converter.infrastructure.converter_repository import ConverterRepository


class InfrastructureModule(Module):
    @provider(scope="request")
    def provide_converter_queries(self, logger: LoggerABC) -> ConverterRepositoryABC:
        return ConverterRepository(logger)

    @provider(scope="singleton")
    def provide_converter_files_repository(
        self,
        logger: LoggerABC,
        cloudinary_client: CloudinaryClient,
    ) -> Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]:
        return ConverterFilesRepository(cloudinary_client, logger)
