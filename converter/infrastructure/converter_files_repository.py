import pathlib
from typing import Final, final

from pydantic import HttpUrl
from types_linq import Enumerable

from common.infrastructure.abc.files_repository_abc import FilesRepositoryABC
from common.core.abc.logger_abc import LoggerABC
from common.core.result import ContextResult, as_awaitable_result
from common.infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from common.infrastructure.cloudinary.schemas import GetFilesResponse


@final
class ConverterFilesRepository(FilesRepositoryABC):
    def __init__(self, cloudinary_client: CloudinaryClient, logger: LoggerABC) -> None:
        self.__cloudinary_client: Final[CloudinaryClient] = cloudinary_client
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aupload_file(self, user_id: str, relative_file_path: str, content: bytes) -> ContextResult[HttpUrl]:
        root = self._get_root_folder_path(user_id)
        relative = pathlib.PurePosixPath(relative_file_path)
        dirname = relative.parent.as_posix()
        folder = f"{root}/{dirname}" if dirname and dirname != "." else root
        public_id = f"{folder}/{relative.name}"
        return await self.__cloudinary_client.aupload_file(folder, public_id, content).map(lambda response: response.secure_url)

    @as_awaitable_result
    async def aget_zip(self, user_id: str, relative_folder_path: str) -> ContextResult[HttpUrl]:
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
        return await (
            self.aget_files(user_id, relative_folder_path)
            .map(lambda response: Enumerable(response.files).select(lambda file: file.public_id))
            .abind(self.__cloudinary_client.adelete_files)
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

    # async def adelete_all_folders(self) -> None:
    #       users_folders: list[str] = self.get_all_users_folders()
    #
    #       total_deleted_folders: int = 0
    #
    #       for i, user_folder in enumerate(users_folders):
    #           await self.adelete_editor_images(user_folder)
    #           await self.adelete_converted_images(user_folder)
    #           self.delete_user_folder(user_folder)
    #
    #           total_deleted_folders += i + 1
    #
    #       self.__logger.log_info(f"Deleted {total_deleted_folders} user folders in Cloudinary storage")
    #       raise NotImplementedError()

    # def get_all_users_folders(self) -> list[str]:
    #       response: Response = cloudinary.api.root_folders()
    #       return [folder["path"] for folder in response["folders"]]
    #       raise NotImplementedError()
