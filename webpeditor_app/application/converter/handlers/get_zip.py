from typing import Annotated, final, Final

from webpeditor_app.application.common.abc.files_repository_abc import FilesRepositoryABC
from webpeditor_app.application.common.files_repository.converter_files_repository import ConverterFilesRepository
from webpeditor_app.application.common.session.session_service import SessionService
from webpeditor_app.application.converter.handlers.schemas.download import GetZipResponse
from webpeditor_app.core.result.context_result import ContextResult
from webpeditor_app.core.result.decorators import as_awaitable_result
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.core.logger import LoggerABC


@final
class GetZip:
    def __init__(
        self,
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        converter_repo: ConverterRepositoryABC,
        logger: LoggerABC,
    ) -> None:
        self.__converter_files_repo: Final[Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]] = converter_files_repo
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def ahandle(self, session_service: SessionService) -> ContextResult[GetZipResponse]:
        return await session_service.asynchronize().abind(self.__aget_zip)

    @as_awaitable_result
    async def __aget_zip(self, user_id: str) -> ContextResult[GetZipResponse]:
        return await self.__converter_files_repo.aget_zip_folder(user_id, "converted").map(
            lambda zip_url: GetZipResponse(zip_url=str(zip_url))
        )
