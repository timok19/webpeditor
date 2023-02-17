import shutil
from pathlib import Path
from typing import Tuple


def delete_empty_folders(media_root: Path) -> None:
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
