from pydantic import BaseModel, ConfigDict


class UploadFileParams(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    relative_folder_path: str
    basename: str
    content: bytes
