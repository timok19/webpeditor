from ninja import Schema
from pydantic import ConfigDict


class DownloadAllZipResponse(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    zip_file_url: str
