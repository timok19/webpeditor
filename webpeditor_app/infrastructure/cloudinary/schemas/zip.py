from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class GenerateZipResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, populate_by_name=True)

    secure_url: HttpUrl = Field(alias="secure_url")
