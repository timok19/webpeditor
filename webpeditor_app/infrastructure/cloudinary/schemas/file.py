from ninja import Field
from pydantic import BaseModel, ConfigDict, HttpUrl


class GetFilesResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, populate_by_name=True)

    total_count: int = Field(alias="total_count")
    files: list["GetFilesResponse.FileData"] = Field(alias="resources")

    class FileData(BaseModel):
        model_config = ConfigDict(frozen=True, strict=True, populate_by_name=True)

        asset_id: str = Field(alias="asset_id")
        public_id: str = Field(alias="public_id")
        created_at: str = Field(alias="created_at")
        format: str = Field(alias="format")
        bytes: int = Field(alias="bytes")
        width: int = Field(alias="width")
        height: int = Field(alias="height")
        asset_folder: str = Field(alias="asset_folder")
        secure_url: HttpUrl = Field(alias="secure_url")


class DeleteFileResponse(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, populate_by_name=True)

    deleted: dict[str, str] = Field(alias="deleted")
