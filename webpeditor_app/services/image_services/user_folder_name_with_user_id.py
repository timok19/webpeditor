from pathlib import Path
from webpeditor import settings


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
