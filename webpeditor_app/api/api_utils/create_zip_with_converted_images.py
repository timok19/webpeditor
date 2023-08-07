import cloudinary.utils


def create_zip_with_converted_images(public_ids: list[str]) -> str:
    cloudinary_parameters: dict = {
        "public_ids": public_ids,
        "resource_type": "image",
    }
    response = cloudinary.utils.download_zip_url(**cloudinary_parameters)

    return response
