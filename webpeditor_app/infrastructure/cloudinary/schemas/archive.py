from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class GenerateArchiveResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, serialize_by_alias=True)

    secure_url: HttpUrl = Field(serialization_alias="secure_url")
