from datetime import datetime

from ninja import Field
from pydantic import BaseModel, ConfigDict


class GetResourcesResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, serialize_by_alias=True)

    resources: list["GetResourcesResponse.ResourceData"] = Field(serialization_alias="resources")

    class ResourceData(BaseModel):
        model_config = ConfigDict(frozen=True, serialize_by_alias=True)

        asset_id: str = Field(serialization_alias="asset_id")
        public_id: str = Field(serialization_alias="public_id")
        created_at: datetime = Field(serialization_alias="created_at")
        format: str = Field(serialization_alias="format")
        bytes: int = Field(serialization_alias="bytes")
        width: int = Field(serialization_alias="width")
        height: int = Field(serialization_alias="height")
        asset_folder: str = Field(serialization_alias="asset_folder")
        url: str = Field(serialization_alias="url")
        secure_url: str = Field(serialization_alias="secure_url")
