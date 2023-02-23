import base64

from pathlib import Path


def convert_url_to_base64(original_image_path: Path, image_content_type: str) -> str:
    """

    Args:
        original_image_path (Path): image object from local
        image_content_type (str): image content type

    Returns:
        uploaded_image_url: uploaded_image_url is an url for image
    """
    image_file: bytes = bytes()

    try:
        with open(original_image_path, "rb") as f:
            image_file = f.read()
    except FileNotFoundError or FileExistsError as e:
        print(e)

    original_image_base64_data = base64.b64encode(image_file)
    uploaded_image_url = (f"data:{image_content_type};base64,"
                          f"{original_image_base64_data.decode('utf-8')}")

    return uploaded_image_url
