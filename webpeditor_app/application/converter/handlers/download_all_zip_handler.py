from typing import final, Final

from webpeditor_app.application.common.abc.converter_files_repository_abc import ConverterFilesRepositoryABC
from webpeditor_app.application.common.session_service import SessionService
from webpeditor_app.application.converter.handlers.schemas import DownloadAllZipResponse
from webpeditor_app.core.result.context_result import ContextResult
from webpeditor_app.core.result.decorators import as_awaitable_result
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.core.logger import LoggerABC


@final
class DownloadAllZipHandler:
    def __init__(
        self,
        converter_files_repository: ConverterFilesRepositoryABC,
        converter_repo: ConverterRepositoryABC,
        user_repo: UserRepositoryABC,
        logger: LoggerABC,
    ) -> None:
        self.__converter_files_repository: Final[ConverterFilesRepositoryABC] = converter_files_repository
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo
        self.__user_repo: Final[UserRepositoryABC] = user_repo
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def ahandle(self, session_service: SessionService) -> ContextResult[DownloadAllZipResponse]:
        return await session_service.asynchronize().abind(self.__adownload_all_zip)

    @as_awaitable_result
    async def __adownload_all_zip(self, user_id: str) -> ContextResult[DownloadAllZipResponse]:
        ...
        # await self.__converter_repo.aget_asset(user_id)
