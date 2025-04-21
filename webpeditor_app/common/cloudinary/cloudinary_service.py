from dataclasses import dataclass
from typing import Any, Callable, final

import cloudinary.api
from cloudinary.api_client.execute_request import Response

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient


@final
@dataclass
class CloudinaryService(CloudinaryServiceABC):
    cloudinary_client: CloudinaryClient
    logger: WebPEditorLoggerABC

    # TODO: rework implementation according new folder structure
    # TODO: rewrite into async using "aiohttp" client

    async def delete_assets(
        self,
        user_id: str,
        filter_func: Callable[[dict[str, Any]], bool] | None = None,
    ) -> None:
        get_resources_response = await self.cloudinary_client.get_resources(user_id)

        for resource in get_resources_response.resources:
            print(resource)

            # if filter_func is None or filter_func(resources):
            #     cloudinary.api.delete_resources([resources["public_id"]])

        self.logger.log_info(f"Assets have been deleted for user '{user_id}'")

    def delete_user_assets_in_subfolder(self, user_id: str, subfolder: str) -> None:
        self.delete_assets(user_id, lambda asset: subfolder in asset["public_id"])

    def delete_user_folder(self, user_id: str) -> None:
        cloudinary.api.delete_folder(user_id)
        self.logger.log_info(f"Folder '{user_id}' and its content have been deleted")

        # response = cloudinary.api.subfolders(folder_path)
        # for folder in response['folders']:
        #     delete_cloudinary_folder(folder['path'])

    def delete_all_folders(self) -> None:
        users_folders: list[str] = self.get_all_users_folders()

        total_deleted_folders: int = 0

        for i, user_folder in enumerate(users_folders):
            self.delete_original_and_edited_images(user_folder)
            self.delete_converted_images(user_folder)
            self.delete_user_folder(user_folder)

            total_deleted_folders += i + 1

        self.logger.log_info(f"Deleted {total_deleted_folders} user folders in Cloudinary storage")

    def get_all_users_folders(self) -> list[str]:
        response: Response = cloudinary.api.root_folders()
        return [folder["path"] for folder in response["folders"]]

    def delete_original_and_edited_images(self, user_id: str) -> None:
        self.delete_user_assets_in_subfolder(user_id, "edited/")
        self.delete_assets(user_id)

    def delete_converted_images(self, user_id: str) -> None:
        self.delete_user_assets_in_subfolder(user_id, "converted/")
