from ninja import Schema
from pydantic import ConfigDict


class ZipConvertedImagesResponse(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    zip_url: str
