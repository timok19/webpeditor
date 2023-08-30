import logging
from typing import List

import cloudinary.api


class CloudinaryService:
    logging.basicConfig(level=logging.INFO)

    # TODO: add other cloudinary method for adding images etc

    @staticmethod
    def delete_all_assets_in_root_folder(user_folder_name: str):
        number_of_deleted_assets: int = 0

        try:
            assets = cloudinary.api.resources(folder=user_folder_name, max_results=500)

            for i, asset in enumerate(assets["resources"]):
                number_of_deleted_assets += i
                cloudinary.api.delete_resources([asset["public_id"]])

            logging.info(
                f"{number_of_deleted_assets} assets "
                f"have been deleted in {user_folder_name} folder"
            )

        except cloudinary.api.NotFound as e:
            logging.error(e)
            pass

    @staticmethod
    def delete_all_assets_in_subfolder(user_folder_name: str, user_subfolder_name: str):
        """
        Deletes assets located in a specific subfolder of a user's folder in Cloudinary.

        Parameters:
            user_folder_name (str):
                The name of the user's folder where assets are stored.
            user_subfolder_name (str):
                The name of the subfolder within the user's folder where the assets to be deleted are located.

        Returns:
            None
        """

        number_of_deleted_assets: int = 0

        try:
            assets = cloudinary.api.resources(folder=user_folder_name, max_results=500)
            for i, asset in enumerate(assets["resources"]):
                if user_subfolder_name in asset["public_id"]:
                    number_of_deleted_assets += i
                    cloudinary.api.delete_resources([asset["public_id"]])

            logging.info(
                f"{number_of_deleted_assets} assets "
                f"have been deleted in {user_folder_name}/{user_subfolder_name} folder"
            )

        except cloudinary.api.NotFound as e:
            logging.error(e)
            pass

    @staticmethod
    def delete_folder(user_folder_name: str):
        try:
            cloudinary.api.delete_folder(user_folder_name)
            logging.info(f"Folder {user_folder_name} and its content have been deleted")

            # TODO: check if deleted subfolder's content as well
            # response = cloudinary.api.subfolders(folder_path)
            # for folder in response['folders']:
            #     delete_cloudinary_folder(folder['path'])

        except cloudinary.api.NotFound:
            logging.error(f"Folder {user_folder_name} not found")
            pass

    @staticmethod
    def get_all_folders() -> List[str]:
        user_folders: list[str] = []

        response = cloudinary.api.root_folders()
        for folder in response["folders"]:
            user_folders.append(folder["path"])

        return user_folders

    @classmethod
    def delete_all_folders(cls):
        number_of_deleted_folders: int = 0
        user_folders = cls.get_all_folders()

        for i, user_folder in enumerate(user_folders):
            cls.delete_original_and_edited_images(user_folder)
            cls.delete_converted_images(user_folder)
            cls.delete_folder(user_folder)
            number_of_deleted_folders += i

        logging.info(
            f"{number_of_deleted_folders} user folders "
            f"has been deleted in Cloudinary storage"
        )

    @classmethod
    def delete_original_and_edited_images(cls, user_folder_name: str):
        cls.delete_all_assets_in_subfolder(user_folder_name, "edited/")
        cls.delete_all_assets_in_root_folder(user_folder_name)

    @classmethod
    def delete_converted_images(cls, user_folder_name: str):
        cls.delete_all_assets_in_subfolder(user_folder_name, "converted/")
