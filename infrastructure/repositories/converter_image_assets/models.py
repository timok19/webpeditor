from pydantic import BaseModel, ConfigDict

from application.common.services.models.file_info import ImageFileInfo
from domain.common.models import ImageAssetFile


class CreateAssetFileParams[T: ImageAssetFile](BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    file_type: type[T]
    file_info: ImageFileInfo
    file_url: str
