from abc import ABC, abstractmethod
from typing import Optional

from PIL.ImageFile import ImageFile

from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.extensions.result_extensions import ContextResult


class ImageFileUtilityABC(ABC):
    @abstractmethod
    def convert_to_bytes(self, file_base64: str) -> ContextResult[bytes]: ...

    @abstractmethod
    async def get_file_content_async(self, file_url: str) -> ContextResult[bytes]: ...

    @abstractmethod
    def get_file_info(self, image_file: ImageFile) -> ContextResult[ImageFileInfo]: ...

    @abstractmethod
    def update_filename(self, image_file: ImageFile, new_filename: str) -> ContextResult[ImageFile]: ...

    @abstractmethod
    def validate_filename(self, filename: Optional[str]) -> ContextResult[str]: ...

    @abstractmethod
    def sanitize_filename(self, filename: str) -> str: ...

    @abstractmethod
    def trim_filename(self, filename: str, *, max_length: int) -> ContextResult[str]: ...
