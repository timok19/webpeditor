import logging
from typing import List

import cloudinary.api

logging.basicConfig(level=logging.INFO)


def delete_assets_in_specific_user_folder(folder_path: str, asset_folder: str):
    try:
        assets = cloudinary.api.resources(folder=folder_path, max_results=500)
        for asset in assets['resources']:
            if asset_folder in asset['public_id']:
                cloudinary.api.delete_resources([asset['public_id']])
                logging.info(f"Asset(s) has/have been deleted from {folder_path}")

    except cloudinary.api.NotFound as e:
        logging.error(e)
        pass


def delete_original_asset(folder_path: str):
    try:
        assets = cloudinary.api.resources(folder=folder_path, max_results=500)

        for asset in assets['resources']:
            cloudinary.api.delete_resources([asset['public_id']])
            logging.info(f"Deleted asset from {folder_path}")

    except cloudinary.api.NotFound as e:
        logging.error(e)
        pass


def delete_cloudinary_folder(folder_path: str):
    try:
        cloudinary.api.delete_folder(folder_path)
        logging.info(f"Folder '{folder_path}' and its content have been deleted")

        # response = cloudinary.api.subfolders(folder_path)
        # for folder in response['folders']:
        #     delete_cloudinary_folder(folder['path'])

    except cloudinary.api.NotFound:
        logging.error(f"Folder '{folder_path}' not found")
        pass


def delete_all_cloudinary_folders():
    i = 0
    user_folders: list = get_all_cloudinary_user_folders()
    for user_folder in user_folders:
        delete_cloudinary_original_and_edited_images(user_folder)
        delete_cloudinary_converted_images(user_folder)
        delete_cloudinary_folder(user_folder)
        i += 1

    logging.info(f"Deleted {i} user folders in Cloudinary storage")


def get_all_cloudinary_user_folders() -> List:
    user_folders = []

    response = cloudinary.api.root_folders()
    for folder in response['folders']:
        user_folders.append(folder['path'])
        continue

    return user_folders


def delete_cloudinary_original_and_edited_images(folder_path: str):
    delete_assets_in_specific_user_folder(folder_path, "edited/")
    delete_original_asset(folder_path)


def delete_cloudinary_converted_images(folder_path: str):
    delete_assets_in_specific_user_folder(folder_path, "converted/")
