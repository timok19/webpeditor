from dataclasses import dataclass, field
from typing import Union

from django.core.files.uploadedfile import UploadedFile

from webpeditor.settings import ImageConverterSettings


@dataclass(frozen=True)
class ConversionOptions:
    output_format: Union[ImageConverterSettings.OutputFormats, ImageConverterSettings.OutputFormatsWithAlphaChannel]
    quality: int = field(default=50)

    def __post_init__(self):
        if not (5 <= self.quality <= 100):
            raise ValueError("Quality must be between %r and %r", 5, 100)


@dataclass(frozen=True)
class ConversionRequest:
    user_id: str
    images_files: list[UploadedFile]
    options: ConversionOptions


# TODO: Add properties
@dataclass(frozen=True)
class ConversionResponse:
    pass
