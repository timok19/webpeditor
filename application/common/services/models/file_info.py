from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict


class ImageFileInfo(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    filename_details: "FilenameDetails"
    file_details: "FileDetails"

    @classmethod
    def create(cls, filename_details: "FilenameDetails", file_details: "FileDetails") -> Self:
        return cls(filename_details=filename_details, file_details=file_details)

    class FilenameDetails(BaseModel):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

        fullname: str
        basename: str
        shortname: str

        @classmethod
        def create(cls, fullname: str, basename: str, shortname: str) -> Self:
            return cls(fullname=fullname, basename=basename, shortname=shortname)

    class FileDetails(BaseModel):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

        format: str
        format_description: str
        content: bytes
        size: int
        width: int
        height: int
        aspect_ratio: Decimal
        color_mode: str
        exif_data: dict[str, str]
