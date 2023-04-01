import shutil
import os
import logging
from pathlib import Path
from typing import Tuple

from webpeditor import settings


def delete_empty_folders(media_root: Path):
    empty_folders = find_empty_folders(media_root)
    for folder in empty_folders:
        shutil.rmtree(folder)
        logging.info(f"Deleted empty folder: {folder}")


def delete_folder_by_expiry(media_root: Path):
    folder_list = os.listdir(media_root)
    for folder in folder_list:
        folder_path = os.path.join(media_root, folder)
        try:
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                logging.info("- User's folder deleted successfully\n")
        except Exception as e:
            logging.error(e)


def find_empty_folders(folder: Path) -> Tuple:
    empty_folders = []
    for item in folder.iterdir():
        if item.is_dir():
            sub_folders = find_empty_folders(item)
            empty_folders.extend(sub_folders)
            if not any(sub_folders) and not any(item.iterdir()):
                empty_folders.append(item)

    return tuple(empty_folders)


def create_folder(user_id: str, is_original_image: bool) -> Path:
    original_image_folder_path, edited_image_folder_path = get_media_root_paths(user_id)

    if is_original_image is True and not original_image_folder_path.exists():
        original_image_folder_path.mkdir(parents=True, exist_ok=True)

        return original_image_folder_path

    elif is_original_image is False and not edited_image_folder_path.exists():
        edited_image_folder_path.mkdir(parents=True, exist_ok=True)

        return edited_image_folder_path


def get_media_root_paths(user_id: str) -> tuple[Path, Path]:
    media_root = Path(settings.MEDIA_ROOT)
    original_image_folder_path: Path = media_root / user_id
    edited_image_folder_path: Path = original_image_folder_path / 'edited'

    return original_image_folder_path, edited_image_folder_path
