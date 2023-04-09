import shutil
import os
import logging
from pathlib import Path
from typing import Tuple

from webpeditor import settings

logging.basicConfig(level=logging.INFO)


def delete_users_folder(folder_path: Path):
    if folder_path.exists():
        shutil.rmtree(folder_path)
    else:
        logging.error(f"Error: provided path does not exist {folder_path}")


def delete_folder_by_expiry(media_root: Path):
    """
    Delete folder in case if user_id does not exist in db

    Args:
        media_root: Media root path
    """
    folder_list = os.listdir(media_root)
    for folder in folder_list:
        folder_path = os.path.join(media_root, folder)
        try:
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                logging.info("- User's folder deleted successfully\n")
        except Exception as e:
            logging.error(e)


def delete_empty_folders(media_root: Path):
    empty_folders = find_empty_folders(media_root)
    for folder in empty_folders:
        shutil.rmtree(folder)
        logging.info(f"Deleted empty folder: {folder}")


def find_empty_folders(folder: Path) -> Tuple:
    empty_folders = []
    for item in folder.iterdir():
        if item.is_dir():
            sub_folders = find_empty_folders(item)
            empty_folders.extend(sub_folders)
            if not any(sub_folders) and not any(item.iterdir()):
                empty_folders.append(item)

    return tuple(empty_folders)


def create_folder(user_id: str, is_original_image: bool) -> Path | None:
    original_image_folder_path, edited_image_folder_path = get_media_root_folder_paths(user_id)

    if is_original_image is True and not original_image_folder_path.exists():
        original_image_folder_path.mkdir(parents=True, exist_ok=True)

        return original_image_folder_path

    elif is_original_image is False and not edited_image_folder_path.exists():
        edited_image_folder_path.mkdir(parents=True, exist_ok=True)

        return edited_image_folder_path

    return None


def get_media_root_folder_paths(user_id: str) -> tuple[Path, Path]:
    """
    Get media root paths for original and edited image.

    Args:
        user_id (str): User's id.

    Returns:
        Returns tuple with original and edited image folder paths
    """
    media_root = Path(settings.MEDIA_ROOT)
    original_image_folder_path: Path = media_root / user_id
    edited_image_folder_path: Path = original_image_folder_path / 'edited'

    return original_image_folder_path, edited_image_folder_path
