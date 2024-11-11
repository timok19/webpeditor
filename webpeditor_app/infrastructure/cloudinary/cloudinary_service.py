from dataclasses import asdict
from io import BytesIO
from typing import Any, Callable

import cloudinary.api
import cloudinary.uploader
from cloudinary import CloudinaryImage
from cloudinary.api_client.execute_request import Response
from injector import inject

from webpeditor_app.common.resultant import Resultant, ResultantValue
from webpeditor_app.core.logging.logger_abc import LoggerABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.infrastructure.cloudinary.models import UploadOptions


class CloudinaryService(CloudinaryServiceABC):
    @inject
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: LoggerABC = logger

    def delete_assets(self, user_id: str, filter_func: Callable[[dict[str, Any]], bool] | None = None) -> None:
        assets: Response = cloudinary.api.resources(folder=user_id, max_results=500)

        for asset in assets["resources"]:
            if filter_func is None or filter_func(asset):
                cloudinary.api.delete_resources([asset["public_id"]])

        self.__logger.log_info(f"Assets have been deleted for user '{user_id}'")

    def delete_user_assets_in_subfolder(self, user_id: str, subfolder: str) -> None:
        self.delete_assets(user_id, filter_func=lambda asset: subfolder in asset["public_id"])

    def delete_user_folder(self, user_id: str) -> None:
        cloudinary.api.delete_folder(user_id)
        self.__logger.log_info(f"Folder '{user_id}' and its content have been deleted")

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

        self.__logger.log_info(f"Deleted {total_deleted_folders} user folders in Cloudinary storage")

    def get_all_users_folders(self) -> list[str]:
        response: Response = cloudinary.api.root_folders()
        return [folder["path"] for folder in response["folders"]]

    def delete_original_and_edited_images(self, user_id: str) -> None:
        self.delete_user_assets_in_subfolder(user_id, "edited/")
        self.delete_assets(user_id)

    def delete_converted_images(self, user_id: str) -> None:
        self.delete_user_assets_in_subfolder(user_id, "converted/")

    def upload_image(self, file_buffer: BytesIO, *, options: UploadOptions) -> ResultantValue[CloudinaryImage]:
        cloudinary_image: CloudinaryImage = cloudinary.uploader.upload_image(file_buffer, **asdict(options))
        return Resultant.success(cloudinary_image)
