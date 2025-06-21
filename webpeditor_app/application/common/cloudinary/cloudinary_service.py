from typing import Final, final

from types_linq.enumerable import Enumerable

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.core.result import ContextResult, acontext_result, ErrorContext
from webpeditor_app.globals import Unit
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient


@final
class CloudinaryService(CloudinaryServiceABC):
    def __init__(self, cloudinary_client: CloudinaryClient, logger: WebPEditorLoggerABC) -> None:
        self.__cloudinary_client: Final[CloudinaryClient] = cloudinary_client
        self.__logger: Final[WebPEditorLoggerABC] = logger

    @acontext_result
    async def aupload_file(self, public_id: str, file_content: bytes) -> ContextResult[str]:
        return await self.__cloudinary_client.aupload_file(public_id, file_content).map(lambda res: str(res.secure_url))

    @acontext_result
    async def adelete_files(self, user_id: str, relative_folder_path: str) -> ContextResult[Unit]:
        def log_success(unit: Unit) -> Unit:
            self.__logger.log_info(f"File has been deleted for user '{user_id}'")
            return unit

        def log_error(error: ErrorContext) -> ErrorContext:
            self.__logger.log_error(f"Failed to delete file for user '{user_id}'")
            return error

        return (
            await self.__cloudinary_client.aget_resources(user_id, relative_folder_path)
            .map(lambda response: Enumerable(response.resources))
            .map(lambda resources: resources.select(lambda resource: resource.public_id).to_list())
            .abind(self.__cloudinary_client.adelete_resources)
            .match(log_success, log_error)
        )

    # TODO
    def delete_user_folder(self, user_id: str) -> None:
        # cloudinary.api.delete_folder(user_id)
        # self.__logger.log_info(f"Folder '{user_id}' and its content have been deleted")

        # response = cloudinary.api.subfolders(folder_path)
        # for folder in response['folders']:
        #     delete_cloudinary_folder(folder['path'])
        raise NotImplementedError()

    async def adelete_all_folders(self) -> None:
        # users_folders: list[str] = self.get_all_users_folders()
        #
        # total_deleted_folders: int = 0
        #
        # for i, user_folder in enumerate(users_folders):
        #     await self.adelete_editor_images(user_folder)
        #     await self.adelete_converted_images(user_folder)
        #     self.delete_user_folder(user_folder)
        #
        #     total_deleted_folders += i + 1
        #
        # self.__logger.log_info(f"Deleted {total_deleted_folders} user folders in Cloudinary storage")
        raise NotImplementedError()

    def get_all_users_folders(self) -> list[str]:
        # response: Response = cloudinary.api.root_folders()
        # return [folder["path"] for folder in response["folders"]]
        raise NotImplementedError()

    async def adelete_editor_images(self, user_id: str) -> None:
        # await self.adelete_files(user_id, subfolder="edited/")
        # await self.adelete_files(user_id)
        raise NotImplementedError()

    async def adelete_converted_images(self, user_id: str) -> None:
        # await self.adelete_files(user_id, subfolder="converted/")
        raise NotImplementedError()
