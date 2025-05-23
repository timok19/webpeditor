from abc import ABC, abstractmethod
from typing import Optional, Union

from PIL.ImageFile import ImageFile

from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import ContextResult


class ImageFileUtilityABC(ABC):
    @abstractmethod
    def to_bytes(self, file_base64: str) -> ContextResult[bytes]: ...

    @abstractmethod
    async def aget_file_content(self, file_url: str) -> ContextResult[bytes]: ...

    @abstractmethod
    def get_file_info(self, image: ImageFile) -> ContextResult[ImageFileInfo]: ...

    @abstractmethod
    def update_filename(self, image: ImageFile, new_filename: str) -> ContextResult[ImageFile]: ...

    @abstractmethod
    def normalize_filename(self, filename: Optional[Union[str, bytes]]) -> ContextResult[str]: ...

    @abstractmethod
    def trim_filename(self, filename: Optional[Union[str, bytes]], max_length: int) -> ContextResult[str]: ...

    @abstractmethod
    def close_file(self, image: ImageFile) -> ContextResult[None]: ...
