from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class UploadImageResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, serialize_by_alias=True)

    asset_id: str = Field(serialization_alias="asset_id")
    secure_url: HttpUrl = Field(serialization_alias="secure_url")
