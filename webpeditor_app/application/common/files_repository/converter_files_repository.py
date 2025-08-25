from typing import Final, final

from webpeditor_app.application.common.abc.converter_files_repository_abc import ConverterFilesRepositoryABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.globals import Unit
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient


@final
class ConverterFilesRepository(ConverterFilesRepositoryABC):
    def __init__(self, cloudinary_client: CloudinaryClient, logger: LoggerABC) -> None:
        self.__cloudinary_client: Final[CloudinaryClient] = cloudinary_client
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aupload_original(self, user_id: str, filename: str, content: bytes) -> ContextResult[str]:
        public_id = f"{self._get_root_path(user_id)}/original/{filename}"
        return await self.__cloudinary_client.aupload_file(public_id, content).map(lambda response: str(response.secure_url))

    @as_awaitable_result
    async def aupload_converted(self, user_id: str, filename: str, content: bytes) -> ContextResult[str]:
        public_id = f"{self._get_root_path(user_id)}/converted/{filename}"
        return await self.__cloudinary_client.aupload_file(public_id, content).map(lambda response: str(response.secure_url))

    @as_awaitable_result
    async def acleanup(self, user_id: str) -> ContextResult[Unit]:
        folder_path = self._get_root_path(user_id)
        return await (
            self.__cloudinary_client.adelete_folder_recursively(folder_path)
            .map(lambda response: self.__logger.info(f"Deleted {len(response.deleted.values())} files from '{folder_path}'", depth=5))
            .to_unit()
        )

    # TODO
    @as_awaitable_result
    async def aget_zip(self, user_id: str) -> ContextResult[str]:
        ...
        # return await self.__cloudinary_client.

    @staticmethod
    def _get_root_path(user_id: str) -> str:
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
