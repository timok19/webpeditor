import base64
from io import BytesIO
from typing import List, Tuple

from PIL import Image
from PIL.Image import Image as ImageClass
from django.core.files.uploadedfile import UploadedFile

from webpeditor_app.services.image_services.image_service import get_file_extension


def convert_images(images_files: list[UploadedFile], output_format: str) -> List[Tuple]:
    """
    Covert image formats into chosen one by user

    Args:
        images_files: Image files from the form
        output_format: The format, that images should be converted

    Returns:
        Returns error about image conversion or converted list of image files
    """

    converted_images = []

    for image_file in images_files:
        try:
            pil_image = Image.open(image_file)
            buffer = BytesIO()

            file_extension: str = get_file_extension(image_file.name).upper()
            if file_extension == 'JPG':
                file_extension = 'JPEG'

            image_file_converted = convert_rgba_image_with_background(pil_image, file_extension, output_format)

            image_file_converted.save(buffer, format=output_format, quality=100)
        except Exception as e:
            raise e

        converted_image = base64.b64encode(buffer.getvalue()).decode()
        img_data = f'data:image/{output_format.lower()};base64,{converted_image}'
        new_filename = f'webpeditor_{image_file.name.rsplit(".", 1)[0]}.{output_format.lower()}'
        converted_images.append((img_data, new_filename))

    return converted_images


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
            - white_background: The rgba_image converted to RGB with a white background if the input format is 'WEBP' or 'PNG' and the output format is different.
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
