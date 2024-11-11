from dataclasses import dataclass
from decimal import Decimal
from typing import NotRequired, TypedDict, Union, Optional


class ExifData(TypedDict):
    tag_id: NotRequired[Union[int, float, str]]
    value: NotRequired[Union[int, float, str]]


@dataclass(frozen=True)
class ImageFileInfo:
    file_format: str
    file_format_description: Optional[str]
    size: int
    resolution: tuple[int, int]
    aspect_ratio: Decimal
    color_mode: str
    exif_data: ExifData
