import base64

from webpeditor_app.models.database.models import OriginalImage


def convert_url_to_base64(image_is_exist: bool, original_image: OriginalImage) -> tuple:
    """

    Args:
        image_is_exist: status for image on image_upload_view
        original_image: image object from db

    Returns:
        uploaded_image_url: uploaded_image_url is an url for the image

                            image_is_exist is an output status
    """
    try:
        with open(original_image.original_image_url.path, 'rb') as file:
            original_image_data = file.read()
    except FileNotFoundError or FileExistsError:
        image_is_exist = False

    original_image_base64_data = base64.b64encode(original_image_data)
    uploaded_image_url = (f"data:{original_image.content_type};base64,"
                          f"{original_image_base64_data.decode('utf-8')}")

    return image_is_exist, uploaded_image_url
