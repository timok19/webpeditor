import shutil
import os
from pathlib import Path
from typing import Tuple

from webpeditor import settings


def delete_empty_folders(media_root: Path):
    """
    Recursively deletes all empty folders in MEDIA_ROOT.
    """
    empty_folders = find_empty_folders(media_root)
    for folder in empty_folders:
        shutil.rmtree(folder)
        print(f"Deleted empty folder: {folder}")


def delete_expire_users_folder(media_root: Path):
    list_of_folders = os.listdir(media_root)
    for folder in list_of_folders:
        folder_path = os.path.join(media_root, folder)
        try:
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print("- User's folder deleted successfully\n")
        except Exception as e:
            print(e)


def find_empty_folders(folder: Path) -> Tuple:
    """
    Returns a tuple with all empty subfolders of the given folder and their subdirectories.
    """
    empty_folders = []
    for item in folder.iterdir():
        if item.is_dir():
            sub_folders = find_empty_folders(item)
            empty_folders.extend(sub_folders)
            if not any(sub_folders) and not any(item.iterdir()):
                empty_folders.append(item)
    return tuple(empty_folders)


def create_new_folder(user_id: str, uploaded_image_folder_status: bool) -> Path:
    """Create a folder named as user_id within the media root directory.

    Parameters:
        user_id (str): Session ID of the current session.
        uploaded_image_folder_status (bool): Create folder for newly uploaded image

    Returns:
        Path(s): Path to the folder named as session_id.
    """
    uploaded_image_folder_path, edited_image_folder_path = get_media_root_paths(user_id)

    if uploaded_image_folder_status is True and not uploaded_image_folder_path.exists():
        uploaded_image_folder_path.mkdir(parents=True, exist_ok=True)
        return uploaded_image_folder_path
    elif uploaded_image_folder_status is False and not edited_image_folder_path.exists():
        edited_image_folder_path.mkdir(parents=True, exist_ok=True)
        return edited_image_folder_path


def get_media_root_paths(user_id: str) -> tuple[Path, Path]:
    media_root = Path(settings.MEDIA_ROOT)
    folder_path_with_uploaded_image: Path = media_root / user_id
    folder_path_with_edited_images: Path = folder_path_with_uploaded_image / 'edited'

    return folder_path_with_uploaded_image, folder_path_with_edited_images