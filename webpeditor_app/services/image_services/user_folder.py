import shutil
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


def create_folder_name_with_user_id(user_id: str) -> Path:
    """Create a folder named as user_id within the media root directory.

    Parameters:
        user_id (str): Session ID of the current session.

    Returns:
        Path: Path to the folder named as session_id.
    """
    media_root = Path(settings.MEDIA_ROOT)
    folder_path_with_uploaded_images = media_root / user_id
    folder_path_with_uploaded_images.mkdir(parents=True, exist_ok=True)

    return Path(folder_path_with_uploaded_images)
