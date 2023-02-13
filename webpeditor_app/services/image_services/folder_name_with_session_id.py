from pathlib import Path
from webpeditor import settings


def create_folder_name_with_user_token(user_token: str) -> Path:
    """Create a folder named as user_token within the media root directory.

    Parameters:
        user_token (str): Generated token for user.

    Returns:
        Path: Path to the folder named as user_token.
    """
    media_root = Path(settings.MEDIA_ROOT)
    folder_path_with_uploaded_images = media_root / user_token
    folder_path_with_uploaded_images.mkdir(parents=True, exist_ok=True)

    return folder_path_with_uploaded_images
