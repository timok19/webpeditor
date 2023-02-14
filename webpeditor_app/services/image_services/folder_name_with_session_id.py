from pathlib import Path
from webpeditor import settings


def create_folder_name_with_session_id(session_id: str) -> Path:
    """Create a folder named as session_id within the media root directory.

    Parameters:
        session_id (str): Session ID of the current session.

    Returns:
        Path: Path to the folder named as session_id.
    """
    media_root = Path(settings.MEDIA_ROOT)
    folder_path_with_uploaded_images = media_root / session_id
    folder_path_with_uploaded_images.mkdir(parents=True, exist_ok=True)

    return Path(folder_path_with_uploaded_images)
