from typing import Annotated, Final, final

from django.http import HttpRequest

from application.common.services.session_service_factory import SessionServiceFactory
from application.converter.commands.schemas.download import GetZipResponse
from core.result.context_result import ContextResult, as_awaitable_result
from infrastructure.abc.converter_image_assets_repository_abc import ConverterImageAssetsRepositoryABC
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from infrastructure.repositories.converter_files.converter_files_repository import ConverterFilesRepository


@final
class GetConvertedZipQuery:
    def __init__(
        self,
        session_service_factory: SessionServiceFactory,
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        converter_repo: ConverterImageAssetsRepositoryABC,
    ) -> None:
        self.__session_service_factory: Final[SessionServiceFactory] = session_service_factory
        self.__converter_files_repo: Final[Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]] = converter_files_repo
        self.__converter_repo: Final[ConverterImageAssetsRepositoryABC] = converter_repo

    @as_awaitable_result
    async def ahandle(self, http_request: HttpRequest) -> ContextResult[GetZipResponse]:
        return await (
            self.__session_service_factory.create(http_request)
            .aget_user_id()
            .abind(lambda user_id: self.__converter_files_repo.azip_folder(user_id, "converted"))
            .map(lambda zip_url: GetZipResponse(zip_url=str(zip_url)))
        )
