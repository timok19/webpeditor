import base64
import logging
import os
from io import BytesIO
from typing import Tuple

import requests
from PIL import Image as PilImage
from PIL.ExifTags import TAGS
from PIL.Image import Image as ImageClass
from PIL.TiffImagePlugin import IFDRational
from _decimal import ROUND_UP, Decimal


logging.basicConfig(level=logging.INFO)


def data_url_to_binary(data_url: str) -> BytesIO:
    data_url = data_url.split(",")[1]
    image_data = base64.b64decode(data_url)

    return BytesIO(image_data)


def get_image_file_instance(image_data: BytesIO) -> ImageClass | None:
    try:
        image_data.seek(0)
        return PilImage.open(image_data)
    except Exception as e:
        logging.error(e)
        return None


def cut_image_name(image_name: str, min_size: int) -> str:
    basename, ext = os.path.splitext(image_name)
    if len(basename) > min_size:
        basename = f"{basename[:(min_size - 3)]}...{basename[-5:]}"

    return basename + ext


def get_image_file_extension(image_name: str) -> str:
    return os.path.splitext(image_name)[1][1:]


def get_image_file_name(image_name: str) -> str:
    return os.path.splitext(image_name)[0]


def get_data_from_image_url(image_url: str | None) -> BytesIO | None:
    if image_url is None:
        return None

    with requests.get(image_url) as response:
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            logging.error(f"Failed to download image: {response.status_code}")
            return None


def get_image_file_size(buffer: BytesIO) -> str:
    size_in_bytes: int = buffer.tell()
    size_in_kb: float = size_in_bytes / 1024

    if size_in_kb >= 1024:
        # Calculate the size in megabytes
        size_in_mb: float = size_in_kb / 1024
        return f"{size_in_mb:.1f} MB"
    else:
        return f"{size_in_kb:.1f} KB"


def get_image_info(image_data: BytesIO) -> None | Tuple:
    def decode_value(value):
        try:
            return value.decode()
        except UnicodeDecodeError:
            return "<undecodable_bytes>"

    buffer = BytesIO()

    image_file = get_image_file_instance(image_data)
    if image_file is None:
        return None

    image_file.save(buffer, format=image_file.format)

    image_format_description = image_file.format_description
    image_size = get_image_file_size(buffer)
    image_resolution = f"{image_file.width}px ⨯ {image_file.height}px"
    image_aspect_ratio = get_image_aspect_ratio(image_file)
    image_mode = image_file.mode
    image_format = image_file.format

    # Get structured exif data, if exists
    exif_data = image_file.getexif()
    if len(exif_data) == 0:
        exif_data = "No exif data was found"
    else:
        exif_data = {
            TAGS.get(tag_id, tag_id): (
                decode_value(exif_data.get(tag_id))
                if isinstance(exif_data.get(tag_id), bytes)
                else int(
                    exif_data.get(tag_id).numerator / exif_data.get(tag_id).denominator
                )
                if isinstance(exif_data.get(tag_id), IFDRational)
                else exif_data.get(tag_id)
            )
            for tag_id in exif_data
        }

    image_file.close()

    return (
        image_format_description,
        image_format,
        image_size,
        image_resolution,
        image_aspect_ratio,
        image_mode,
        exif_data,
    )


def get_image_aspect_ratio(image_file: ImageClass) -> Decimal:
    return Decimal(image_file.width / image_file.height).quantize(
        Decimal(".1"), rounding=ROUND_UP
    )
