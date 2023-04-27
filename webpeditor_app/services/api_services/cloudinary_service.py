import logging
from typing import List

import cloudinary.api

logging.basicConfig(level=logging.INFO)


def delete_assets_in_user_folder(folder_path):
    try:
        assets = cloudinary.api.resources(folder=folder_path, max_results=500)
        for asset in assets['resources']:
            cloudinary.api.delete_resources([asset['public_id']])
            logging.info(f"Deleted asset: {asset['public_id']}")

        # Recursively delete assets in subfolders
        response = cloudinary.api.subfolders(folder_path)
        for folder in response['folders']:
            delete_assets_in_user_folder(folder['path'])

    except cloudinary.api.NotFound as e:
        logging.error(e)
        pass


def delete_user_folder_with_content(folder_path):
    delete_assets_in_user_folder(folder_path)

    # Delete the folder
    try:
        cloudinary.api.delete_folder(folder_path)
        logging.info(f"Folder '{folder_path}' and its content have been deleted")
    except cloudinary.api.NotFound:
        logging.error(f"Folder '{folder_path}' not found")


def delete_all_folders():
    user_folders = get_all_user_folders()

    i = 0
    while i < len(user_folders):
        delete_user_folder_with_content(user_folders[i])
        i += 1

    logging.info(f"Deleted {i} user folders in Cloudinary storage")


def get_all_user_folders() -> List:
    user_folders = []

    response = cloudinary.api.root_folders()
    for folder in response['folders']:
        user_folders.append(folder['path'])
        continue

    return user_folders
