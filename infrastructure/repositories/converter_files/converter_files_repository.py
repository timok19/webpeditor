from typing import Final, final

from pydantic import HttpUrl
from types_linq import Enumerable

from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, as_awaitable_result
from infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from infrastructure.cloudinary.models import GetFilesResponse
from infrastructure.repositories.converter_files.models import UploadFileParams


@final
class ConverterFilesRepository(FilesRepositoryABC):
    def __init__(self, cloudinary_client: CloudinaryClient, logger: LoggerABC) -> None:
        self.__cloudinary_client: Final[CloudinaryClient] = cloudinary_client
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aupload_file(self, user_id: str, *, params: UploadFileParams) -> ContextResult[HttpUrl]:
        folder = f"{self._get_root_folder_path(user_id)}/{params.relative_folder_path}"
        public_id = f"{folder}/{params.basename}"
        return await self.__cloudinary_client.aupload_file(folder, public_id, params.content).map(lambda response: response.secure_url)

    @as_awaitable_result
    async def azip_folder(self, user_id: str, relative_folder_path: str) -> ContextResult[HttpUrl]:
        zip_file_path = f"{self._get_root_folder_path(user_id)}/webpeditor_{relative_folder_path.replace('/', '_')}.zip"
        return (
            await self.aget_files(user_id, relative_folder_path)
            .map(lambda response: Enumerable(response.files).select(lambda resource: resource.public_id))
            .abind(lambda public_ids: self.__cloudinary_client.agenerate_zip_archive(public_ids, zip_file_path))
            .map(lambda response: response.secure_url)
        )

    @as_awaitable_result
    async def adelete_files(self, user_id: str, relative_folder_path: str) -> ContextResult[None]:
        folder_path = f"{self._get_root_folder_path(user_id)}/{relative_folder_path}"

        get_files_response_result = await self.aget_files(user_id, relative_folder_path)
        if get_files_response_result.is_error():
            self.__logger.debug(f"No files to delete at {folder_path}")
            return ContextResult[None].success(None)

        public_ids = Enumerable(get_files_response_result.ok.files).select(lambda file: file.public_id).to_list()
        return await (
            self.__cloudinary_client.adelete_files(public_ids)
            .map(lambda response: self.__logger.info(f"Deleted {len(response.deleted.values())} files from '{folder_path}'"))
            .as_empty()
        )

    @as_awaitable_result
    async def aget_files(self, user_id: str, relative_folder_path: str) -> ContextResult[GetFilesResponse]:
        folder_path = f"{self._get_root_folder_path(user_id)}/{relative_folder_path}"
        return await self.__cloudinary_client.aget_files(folder_path)

    @staticmethod
    def _get_root_folder_path(user_id: str) -> str:
        return f"{user_id}/converter"
