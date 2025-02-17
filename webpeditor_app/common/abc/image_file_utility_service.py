from abc import ABC, abstractmethod
from typing import Optional

from PIL.ImageFile import ImageFile

from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.common.result_extensions import ValueResult


class ImageFileUtilityServiceABC(ABC):
    @abstractmethod
    def convert_to_bytes(self, file_base64: str) -> ValueResult[bytes]: ...

    @abstractmethod
    def trim_filename(self, filename: str, *, max_length: int) -> ValueResult[str]: ...

    @abstractmethod
    async def get_file_content_async(self, file_url: str) -> ValueResult[bytes]: ...

    @abstractmethod
    def get_file_info(self, image_file: ImageFile) -> ValueResult[ImageFileInfo]: ...

    @abstractmethod
    def update_filename(self, image_file: ImageFile, new_filename: str) -> ValueResult[ImageFile]: ...

    @abstractmethod
    def validate_filename(self, filename: Optional[str]) -> ValueResult[str]: ...

    @abstractmethod
    def sanitize_filename(self, filename: str) -> str: ...
