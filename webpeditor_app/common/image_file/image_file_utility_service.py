import base64
import os
import requests

from fractions import Fraction
from io import BytesIO
from typing import Any, Optional, Union

from PIL import ExifTags, Image
from PIL.Image import Exif
from PIL.ImageFile import ImageFile
from PIL.TiffImagePlugin import IFDRational
from decimal import ROUND_UP, Decimal

from rest_framework import status

from webpeditor_app.common.image_file.image_file_utility_service_abc import ImageFileUtilityServiceABC
from webpeditor_app.common.image_file.models import ImageFileInfo, ExifData
from webpeditor_app.common.resultant import ErrorCode, ResultantValue, Resultant


class ImageFileUtilityService(ImageFileUtilityServiceABC):
    def file_base64_to_bytes(self, file_base64: str) -> ResultantValue[bytes]:
        if len(file_base64) == 0:
            return Resultant.error("Invalid image base64", error_code=ErrorCode.INTERNAL_SERVER_ERROR)

        image_base64_data: str = file_base64.split(",")[1]

        return Resultant.success(base64.b64decode(image_base64_data))

    def shorten_filename(self, filename: str, *, max_filename_size: int) -> ResultantValue[str]:
        if max_filename_size <= 0:
            return Resultant.error(f"`max_filename_size` must be greater than 0, got {max_filename_size}", error_code=ErrorCode.INTERNAL_SERVER_ERROR)

        if len(filename) <= max_filename_size:
            return Resultant.success(filename)

        basename, extension = os.path.splitext(filename)

        # Minimum space needed: 3 for ellipsis + length of extension
        min_required_length: int = len(extension) + 3

        if max_filename_size < min_required_length:
            return Resultant.success(f"{basename[:max_filename_size - 3]}...")

        return Resultant.success(f"{basename[:(max_filename_size - min_required_length)]}...{extension}")

    def get_file_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[1][1:]

    def get_file_basename(self, filename: str) -> str:
        return os.path.splitext(filename)[0]

    def get_bytes_from_file_url(self, file_url: str) -> ResultantValue[bytes]:
        with requests.get(file_url) as file_response:
            if file_response.status_code == status.HTTP_404_NOT_FOUND:
                return Resultant.error(
                    f"Unable to get content of image file from url '{file_url}'",
                    error_code=ErrorCode.NOT_FOUND,
                )

            if len(file_response.content) == 0 or file_response.content is None:
                return Resultant.error("File has no content", error_code=ErrorCode.NOT_FOUND)

            return Resultant.success(file_response.content)

    def get_file_info(self, file_buffer: BytesIO) -> ResultantValue[ImageFileInfo]:
        with Image.open(file_buffer) as image_file:
            file_format: Optional[str] = image_file.format
            if file_format is None:
                return Resultant.error("Failed to read image file format", error_code=ErrorCode.INTERNAL_SERVER_ERROR)

            size: int = len(file_buffer.getvalue())
            if size == 0:
                return Resultant.error("File has no content", error_code=ErrorCode.INTERNAL_SERVER_ERROR)

            file_format_description: Optional[str] = image_file.format_description
            resolution: tuple[int, int] = image_file.size
            aspect_ratio: Decimal = self.__get_aspect_ratio_from_resolution(resolution)
            color_mode: str = image_file.mode
            exif_data: ExifData = self.__get_safe_exif_data(image_file)

        return Resultant.success(
            ImageFileInfo(
                file_format=file_format,
                file_format_description=file_format_description,
                size=size,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                color_mode=color_mode,
                exif_data=exif_data,
            )
        )

    @staticmethod
    def __get_aspect_ratio_from_resolution(resolution: tuple[int, int]) -> Decimal:
        aspect_ratio: Decimal = Decimal(resolution[0] / resolution[1])
        rounded_aspect_ratio: Decimal = aspect_ratio.quantize(Decimal(".1"), rounding=ROUND_UP)
        return rounded_aspect_ratio

    def __get_safe_exif_data(self, image_file: ImageFile) -> ExifData:
        exif: Exif = image_file.getexif()

        # If no EXIF data is found, return an empty dictionary
        if not exif or len(exif) == 0:
            return ExifData()

        # Map EXIF tags to human-readable names and decode values where necessary
        mapped_exif_data: ExifData = ExifData(**{ExifTags.TAGS[tag_id]: self.__safely_decode_exif_value(exif[tag_id]) for tag_id in exif})

        return mapped_exif_data

    @staticmethod
    def __safely_decode_exif_value(value: Any) -> Union[int, float, str]:
        """
        Safely decode the EXIF value based on its type.
        Handles `bytes`, `IFDRational`, and other types.
        """

        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        elif isinstance(value, IFDRational):
            return float(Fraction(int(value.numerator), value.denominator))
        elif isinstance(value, (int, float)):
            return value
        else:
            return str(value)
