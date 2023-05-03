import traceback

import cloudinary.uploader

from io import BytesIO
from typing import List, Tuple, Dict
from copy import copy

from PIL import Image
from PIL.Image import Image as ImageClass, Exif
from cloudinary import CloudinaryImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.api_services.cloudinary_service import delete_assets_in_user_folder
from webpeditor_app.services.image_services.image_service import (get_image_file_extension,
                                                                  image_name_shorter,
                                                                  get_image_info,
                                                                  get_converted_image)


def process_image(image_file: InMemoryUploadedFile, quality: int, output_format: str) \
        -> Tuple[ImageClass, ImageClass, BytesIO]:
    pil_image: ImageClass = Image.open(image_file)
    pil_image_exif_data = pil_image.getexif()

    file_extension: str = get_image_file_extension(image_file.name).upper()
    if file_extension == "JPG":
        file_extension = "JPEG"

    image_file_converted: ImageClass = convert_image_format(pil_image, file_extension, output_format)

    buffer = BytesIO()
    image_file_converted.save(buffer, format=output_format, quality=quality, exif=pil_image_exif_data)
    buffer.seek(0)

    return pil_image, image_file_converted, buffer


def save_image_into_cloudinary(image_file: InMemoryUploadedFile,
                               image_bytes: BytesIO,
                               user_id: str,
                               output_format: str) -> Tuple[CloudinaryImage, str]:
    new_image_name = image_name_shorter(
        f'webpeditor_'
        f'{image_file.name.rsplit(".", 1)[0]}.'
        f'{output_format.lower()}',
        32
    )

    cloudinary_options: dict = {
        "folder": f"{user_id}/converted/",
        "use_filename": True,
        "unique_filename": True,
        "filename_override": new_image_name,
        "overwrite": False
    }
    cloudinary_image = cloudinary.uploader.upload_image(image_bytes, **cloudinary_options)

    return cloudinary_image, new_image_name


def update_converted_image_object(user_id: str,
                                  request: WSGIRequest,
                                  image_set: dict):
    converted_image_query_set: QuerySet[ConvertedImage] = ConvertedImage.objects.filter(user_id=user_id)
    converted_image_object: ConvertedImage = converted_image_query_set.first()

    if converted_image_object is None:
        converted_image_object = ConvertedImage(
            user_id=user_id,
            image_set=[image_set],
            session_key=request.session.session_key,
            session_key_expiration_date=request.session.get_expiry_date()
        )
        converted_image_object.save()
    else:
        updated_image_set = copy(converted_image_object.image_set)
        updated_image_set.append(image_set)
        converted_image_query_set.update(image_set=updated_image_set)


def create_image_set(image_id: int,
                     pil_image: ImageClass,
                     image_file_converted: ImageClass,
                     buffer: BytesIO,
                     image_file: InMemoryUploadedFile,
                     cloudinary_image_url: str,
                     new_image_name: str,
                     output_format: str) -> Tuple[Dict, float, float, Exif | str, Exif | str]:
    original_image_file_size: float = round(int(image_file.size) / 1024, 1)
    converted_image_file_size: float = round((len(buffer.getvalue()) / 1024), 1)

    original_image_exif_data: Exif | str = get_image_info(image_file.file)[6]
    converted_image_exif_data: Exif | str = get_image_info(buffer)[6]

    image_set: dict = {
        "image_id": image_id,
        "image_name": new_image_name,
        "image_url": cloudinary_image_url,
        "original_image_data": {
            "content_type": f"image/{str(pil_image.format).lower()}",
            "image_file_size_in_kb": original_image_file_size,
            "image_mode": str(pil_image.mode),
            "image_exif_data": original_image_exif_data,
        },
        "converted_image_data": {
            "content_type": f"image/{output_format.lower()}",
            "image_file_size_in_kb": converted_image_file_size,
            "image_mode": str(image_file_converted.mode),
            "image_exif_data": converted_image_exif_data,
        }
    }

    return (
        image_set,
        original_image_file_size,
        converted_image_file_size,
        original_image_exif_data,
        converted_image_exif_data
    )


def convert_image_format(pil_image: ImageClass, file_extension: str, output_format: str) -> ImageClass:
    """
    Convert an image with an optional white background, depending on the input and output formats.

    Args:
        pil_image (ImageClass): The input image as a PIL Image object.
        file_extension (str): The file extension of the input image (e.g., 'WEBP', 'PNG', 'JPG').
        output_format (str): The desired output format (e.g., 'WEBP', 'PNG', 'JPG').

    Returns:
        ImageClass: The converted image, which can be one of the following:

            - rgba_image: An image with an alpha channel (RGBA) if both input and output formats are 'WEBP' or 'PNG'.
            - image_with_white_background: The rgba_image converted to RGB with a white background
              if the input format is 'WEBP' or 'PNG' and the output format is different.
            - pil_image: The input image converted to RGB if the input format is not 'WEBP' or 'PNG'.
    """

    if file_extension in ['WEBP', 'PNG']:
        rgba_image = pil_image.convert('RGBA')

        if output_format in ['WEBP', 'PNG']:
            return rgba_image

        image_with_white_background = Image.new('RGB', rgba_image.size, (255, 255, 255))
        # Use the alpha channel as a mask
        image_with_white_background.paste(rgba_image, mask=rgba_image.split()[3])

        return image_with_white_background
    else:
        return pil_image.convert('RGB')


def convert_and_save_images(user_id: str,
                            request: WSGIRequest,
                            images_files: List[InMemoryUploadedFile],
                            quality: int,
                            output_format: str) -> List:
    """
    Covert image formats into chosen one by user

    Args:
        user_id: User ID as a name of folder, where will be stored converted image(s)
        request: WSGIRequest
        images_files: Image files from the form
        quality (int): Quality output. Values: 1 - 100
        output_format: The format, that images should be converted

    Returns:
        Returns converted list of image files
    """

    converted_image = get_converted_image(user_id)
    converted_images_list = []
    image_id = 0

    # Delete previous content
    if converted_image:
        converted_image.delete()
        delete_assets_in_user_folder(f"{user_id}/converted/")

    for image_file in images_files:
        image_id += 1

        try:
            pil_image, image_file_converted, buffer = process_image(image_file, quality, output_format)
            cloudinary_image, new_image_name = save_image_into_cloudinary(image_file, buffer, user_id, output_format)

            result: tuple = create_image_set(
                image_id,
                pil_image,
                image_file_converted,
                buffer,
                image_file,
                cloudinary_image.url,
                new_image_name,
                output_format
            )
            image_set: dict = result[0]
            original_image_file_size: float = result[1]
            converted_image_file_size: float = result[2]
            original_image_exif_data: Exif | str = result[3]
            converted_image_exif_data: Exif | str = result[4]

            update_converted_image_object(user_id, request, image_set)

            # Append all data into list of tuples for each image
            converted_images_list.append((
                cloudinary_image.url,
                new_image_name,
                str(pil_image.format).upper(),
                output_format.upper(),
                original_image_file_size,
                converted_image_file_size,
                str(pil_image.mode),
                original_image_exif_data,
                str(image_file_converted.mode),
                converted_image_exif_data
            ))

        except Exception as e:
            print("An error occurred:", e)
            traceback.format_exc()
            raise e

    return converted_images_list
