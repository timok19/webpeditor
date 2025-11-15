from ninja import Schema
from pydantic import ConfigDict


class GetZipResponse(Schema):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    zip_url: str
