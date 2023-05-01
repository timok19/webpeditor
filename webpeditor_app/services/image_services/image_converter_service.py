import cloudinary.uploader

from io import BytesIO
from typing import List, Tuple

from PIL import Image
from PIL.Image import Image as ImageClass
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.api_services.cloudinary_service import delete_assets_in_user_folder
from webpeditor_app.services.image_services.image_service import get_image_file_extension


def convert_and_save_images(user_id: str, request: WSGIRequest, images_files: list[UploadedFile], output_format: str) \
        -> List[Tuple]:
    """
    Covert image formats into chosen one by user

    Args:
        user_id: User ID as a name of folder, where will be stored converted image(s)
        request: WSGIRequest
        images_files: Image files from the form
        output_format: The format, that images should be converted

    Returns:
        Returns error about image conversion or converted list of image files
    """

    converted_image: ConvertedImage | None = ConvertedImage.objects.filter(user_id=user_id).first()
    converted_images_list = []
    image_id = 0

    # Delete previous content
    if converted_image:
        converted_image.delete()
        delete_assets_in_user_folder(f"{user_id}/converted")

    for image_file in images_files:
        image_id += 1
        try:
            pil_image = Image.open(image_file)
            buffer = BytesIO()

            file_extension: str = get_image_file_extension(image_file.name).upper()
            if file_extension == 'JPG':
                file_extension = 'JPEG'

            image_file_converted = convert_rgba_image_with_background(pil_image, file_extension, output_format)

            image_file_converted.save(buffer, format=output_format, quality=100)
            buffer.seek(0)
        except Exception as e:
            raise e

        new_filename = f'webpeditor_{image_file.name.rsplit(".", 1)[0]}.{output_format.lower()}'
        cloudinary_options: dict = {
            "folder": f"{user_id}/converted",
            "use_filename": True,
            "unique_filename": True,
            "filename_override": new_filename,
            "overwrite": False
        }
        cloudinary_image = cloudinary.uploader.upload_image(buffer, **cloudinary_options)

        converted_images_list.append((cloudinary_image.url, new_filename))

        if converted_image is None:
            converted_image = ConvertedImage(
                user_id=user_id,
                image_set=[{
                    "image_id": image_id,
                    "image_name": new_filename,
                    "image_url": cloudinary_image.url,
                    "content_type": f"image/{output_format.lower()}"
                }],
                session_key=request.session.session_key,
                session_key_expiration_date=request.session.get_expiry_date()
            )
            converted_image.save()
        else:
            existing_image_set = converted_image.image_set
            new_image_data = {
                "image_id": image_id,
                "image_name": new_filename,
                "image_url": cloudinary_image.url,
                "content_type": f"image/{output_format.lower()}"
            }
            updated_image_set = existing_image_set.copy()
            updated_image_set.append(new_image_data)

            ConvertedImage.objects.filter(user_id=user_id).update(image_set=updated_image_set)

    return converted_images_list


def convert_rgba_image_with_background(pil_image: ImageClass, file_extension: str, output_format: str) -> ImageClass:
    """
    Convert an image with an optional white background, depending on the input and output formats.

    Args:
        pil_image (ImageClass): The input image as a PIL Image object.
        file_extension (str): The file extension of the input image (e.g., 'WEBP', 'PNG', 'JPG').
        output_format (str): The desired output format (e.g., 'WEBP', 'PNG', 'JPG').

    Returns:
        ImageClass: The converted image, which can be one of the following:

            - rgba_image: An image with an alpha channel (RGBA) if both input and output formats are 'WEBP' or 'PNG'.
            - white_background: The rgba_image converted to RGB with a white background
              if the input format is 'WEBP' or 'PNG' and the output format is different.
            - pil_image: The input image converted to RGB if the input format is not 'WEBP' or 'PNG'.
    """

    if file_extension in ['WEBP', 'PNG']:
        rgba_image = pil_image.convert('RGBA')

        if output_format in ['WEBP', 'PNG']:
            return rgba_image

        white_background = Image.new('RGB', rgba_image.size, (255, 255, 255))
        white_background.paste(rgba_image, mask=rgba_image.split()[3])  # Use the alpha channel as a mask

        return white_background
    else:
        return pil_image.convert('RGB')
