from typing import Final, final

from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import ContextResult, acontext_result
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
    async def adelete_folder_recursively(self, folder_path: str) -> ContextResult[Unit]:
        return await (
            self.__cloudinary_client.adelete_folder_recursively(folder_path)
            .log_result(
                lambda data: self.__logger.log_info(f"Deleted {len(data.deleted.values())} files in the folder '{folder_path}'", depth=5),
                lambda _: None,
            )
            .map(lambda _: Unit())
        )

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
