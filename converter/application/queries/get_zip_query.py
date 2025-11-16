from typing import Annotated, final, Final, Optional

from django.http import HttpRequest
from ninja_extra.context import RouteContext

from common.application.abc.validator_abc import ValidatorABC
from common.application.session.session_service_factory import SessionServiceFactory
from common.infrastructure.abc.files_repository_abc import FilesRepositoryABC
from converter.infrastructure.converter_files_repository import ConverterFilesRepository
from converter.application.commands.schemas.download import GetZipResponse
from common.core.result.context_result import ContextResult, as_awaitable_result
from converter.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC


@final
class GetZipQuery:
    def __init__(
        self,
        route_context_validator: ValidatorABC[RouteContext],
        http_request_validator: ValidatorABC[HttpRequest],
        session_service_factory: SessionServiceFactory,
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        converter_repo: ConverterRepositoryABC,
    ) -> None:
        self.__route_context_validator: Final[ValidatorABC[RouteContext]] = route_context_validator
        self.__http_request_validator: Final[ValidatorABC[HttpRequest]] = http_request_validator
        self.__session_service_factory: Final[SessionServiceFactory] = session_service_factory
        self.__converter_files_repo: Final[Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]] = converter_files_repo
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo

    @as_awaitable_result
    async def ahandle(self, context: Optional[RouteContext]) -> ContextResult[GetZipResponse]:
        return (
            await self.__route_context_validator.validate(context)
            .bind(lambda ctx: self.__http_request_validator.validate(ctx.request))
            .abind(lambda http_request: self.__session_service_factory.create(http_request).aget_user_id())
            .abind(self.__aget_zip)
        )

    @as_awaitable_result
    async def __aget_zip(self, user_id: str) -> ContextResult[GetZipResponse]:
        return await self.__converter_files_repo.aget_zip(user_id, "converted").map(lambda zip_url: GetZipResponse(zip_url=str(zip_url)))
