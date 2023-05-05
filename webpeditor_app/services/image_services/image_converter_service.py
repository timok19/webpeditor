import logging

import cloudinary.uploader
import concurrent.futures

from io import BytesIO
from typing import List, Tuple, Dict
from copy import copy

from PIL import Image as PilImage
from PIL.Image import Image as ImageClass, Exif
from cloudinary import CloudinaryImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.external_api_services.cloudinary_service import delete_cloudinary_converted_images

from webpeditor_app.services.image_services.image_service import (image_name_shorter,
                                                                  get_image_info,
                                                                  get_converted_image,
                                                                  get_image_file_size)


def convert_image(image_file: InMemoryUploadedFile, quality: int, output_format: str) \
        -> Tuple[ImageClass, ImageClass, BytesIO]:
    buffer = BytesIO()
    min_quality, max_quality, max_safe_quality = 1, 100, 95

    pil_image: ImageClass = PilImage.open(image_file)

    pil_image_exif_data = pil_image.getexif()
    pil_image_format: str = pil_image.format

    pil_image_converted: ImageClass = convert_color_mode(pil_image, pil_image_format, output_format)

    if min_quality < quality <= max_quality:
        if output_format == 'JPEG':
            pil_image_converted.save(
                buffer,
                format=output_format,
                quality=quality,
                subsampling=0 if quality == max_quality else None,
                exif=pil_image_exif_data
            )
        elif output_format == 'TIFF':
            pil_image_converted.save(
                buffer,
                format=output_format,
                quality=quality,
                exif=pil_image_exif_data,
                compression="jpeg"
            )
        elif output_format == 'BMP':
            pil_image_converted.save(
                buffer,
                format=output_format,
            )
        else:
            pil_image_converted.save(
                buffer,
                format=output_format,
                quality=max_safe_quality if max_safe_quality < quality <= max_quality else quality,
                exif=pil_image_exif_data
            )
        buffer.seek(0)
    else:
        raise ValueError("Image quality cannot be less than 1")

    return pil_image, pil_image_converted, buffer


def save_image_into_cloudinary(image_bytes: BytesIO,
                               user_id: str,
                               new_image_name: str) -> Tuple[CloudinaryImage, str]:

    cloudinary_options: dict = {
        "folder": f"{user_id}/converted/",
        "use_filename": True,
        "unique_filename": True,
        "filename_override": new_image_name,
        "overwrite": False
    }
    cloudinary_image = cloudinary.uploader.upload_image(image_bytes, **cloudinary_options)

    return cloudinary_image, str(cloudinary_image.public_id)


def update_converted_image(user_id: str,
                           request: WSGIRequest,
                           image_set: dict):
    converted_image_query_set: QuerySet[ConvertedImage] = ConvertedImage.objects.filter(user_id=user_id)
    converted_image: ConvertedImage = converted_image_query_set.first()

    if converted_image is None:
        converted_image = ConvertedImage(
            user_id=user_id,
            image_set=[image_set],
            session_key=request.session.session_key,
            session_key_expiration_date=request.session.get_expiry_date()
        )
        converted_image.save()
    else:
        updated_image_set = copy(converted_image.image_set)
        updated_image_set.append(image_set)
        converted_image_query_set.update(image_set=updated_image_set)


def create_image_set(image_id: int,
                     pil_image: ImageClass,
                     pil_image_converted: ImageClass,
                     converted_image_buffer: BytesIO,
                     original_image_file: InMemoryUploadedFile,
                     cloudinary_image_url: str,
                     new_image_name: str,
                     new_image_name_shorter: str,
                     public_id: str,
                     output_format: str) -> Dict:

    original_image_file_size: str = get_image_file_size(original_image_file.file)
    converted_image_file_size: str = get_image_file_size(converted_image_buffer)

    original_image_exif_data: Exif | str = get_image_info(original_image_file.file)[6]
    converted_image_exif_data: Exif | str = get_image_info(converted_image_buffer)[6]

    image_set: dict = {
        "image_id": image_id,
        "image_name_shorter": new_image_name_shorter,
        "public_id": public_id,
        "image_name": new_image_name,
        "image_url": cloudinary_image_url,
        "original_image_data": {
            "content_type": f"image/{str(pil_image.format).lower()}",
            "image_file_size": original_image_file_size,
            "image_mode": str(pil_image.mode),
            "image_exif_data": original_image_exif_data,
        },
        "converted_image_data": {
            "content_type": f"image/{output_format.lower()}",
            "image_file_size": converted_image_file_size,
            "image_mode": str(pil_image_converted.mode),
            "image_exif_data": converted_image_exif_data,
        }
    }

    return image_set


def convert_color_mode(pil_image: ImageClass, input_file_format: str, output_file_format: str) -> ImageClass:
    image_formats_with_alpha_channel: set[str] = {'WEBP', 'PNG', 'GIF'}

    if input_file_format in image_formats_with_alpha_channel:
        rgba_image = pil_image.convert('RGBA')

        if output_file_format in image_formats_with_alpha_channel:
            return rgba_image

        image_with_white_background = PilImage.new('RGB', rgba_image.size, (255, 255, 255))
        image_with_white_background.paste(rgba_image, mask=rgba_image.split()[3])  # Use the alpha channel as a mask
        return image_with_white_background

    else:
        return pil_image.convert('RGB')


def convert_and_save_image(arguments: Tuple[int, str, WSGIRequest, InMemoryUploadedFile, int, str]) -> Tuple:
    image_id, user_id, request, image_file, quality, output_format = arguments

    try:
        new_image_name: str = f'webpeditor_{image_file.name.rsplit(".", 1)[0]}.{output_format.lower()}'
        new_image_name_shorter: str = image_name_shorter(new_image_name, 25)

        pil_image, pil_image_converted, buffer = convert_image(image_file, quality, output_format)
        cloudinary_image, public_id = save_image_into_cloudinary(buffer, user_id, new_image_name)

        image_set: dict = create_image_set(
            image_id,
            pil_image,
            pil_image_converted,
            buffer,
            image_file,
            cloudinary_image.url,
            new_image_name,
            new_image_name_shorter,
            public_id,
            output_format
        )

        original_image_data: dict = image_set.get("original_image_data")
        converted_image_data: dict = image_set.get("converted_image_data")

        original_image_file_size: str = original_image_data.get("image_file_size")
        converted_image_file_size: str = converted_image_data.get("image_file_size")
        original_image_exif_data: Exif | str = original_image_data.get("image_exif_data")
        converted_image_exif_data: Exif | str = converted_image_data.get("image_exif_data")

        update_converted_image(user_id, request, image_set)

        return (
            cloudinary_image.url,
            new_image_name,
            public_id,
            new_image_name_shorter,
            str(pil_image.format).upper(),
            output_format.upper(),
            original_image_file_size,
            converted_image_file_size,
            str(pil_image.mode),
            original_image_exif_data,
            str(pil_image_converted.mode),
            converted_image_exif_data
        )

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise e


def run_conversion_task(user_id: str,
                        request: WSGIRequest,
                        images_files: List[InMemoryUploadedFile],
                        quality: int,
                        output_format: str) -> List:

    converted_image = get_converted_image(user_id)
    converted_images_list = []

    # Delete previous content if exist
    if converted_image:
        converted_image.delete()
        delete_cloudinary_converted_images(f"{user_id}/converted/")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        args_list = [(i + 1, user_id, request, image_file, quality, output_format)
                     for i, image_file in enumerate(images_files)]

        futures = [executor.submit(convert_and_save_image, arguments) for arguments in args_list]

        for future in concurrent.futures.as_completed(futures):
            try:
                result: tuple = future.result()
                converted_images_list.append(result)
            except Exception as e:
                print(f"An error occurred in a parallel task: {e}")

    return converted_images_list
