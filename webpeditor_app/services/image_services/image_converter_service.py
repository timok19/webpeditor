import base64
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import UploadedFile


def convert_images(images_files: list[UploadedFile], output_format: str) -> list[tuple[str, str]]:
    converted_images = []

    for image_file in images_files:
        img = Image.open(image_file)
        buffer = BytesIO()
        img.save(buffer, format=output_format)

        converted_image = base64.b64encode(buffer.getvalue()).decode()
        img_data = f'data:image/{output_format.lower()};base64,{converted_image}'
        new_filename = f'webpeditor_{image_file.name.rsplit(".", 1)[0]}.{output_format.lower()}'
        converted_images.append((img_data, new_filename))

    return converted_images
