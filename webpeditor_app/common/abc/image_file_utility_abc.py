from abc import ABC, abstractmethod
from typing import Optional

from PIL.ImageFile import ImageFile

from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.based_result import BasedResultOutput


class ImageFileUtilityABC(ABC):
    @abstractmethod
    def convert_to_bytes(self, file_base64: str) -> BasedResultOutput[bytes]: ...

    @abstractmethod
    async def get_file_content_async(self, file_url: str) -> BasedResultOutput[bytes]: ...

    @abstractmethod
    def get_file_info(self, image_file: ImageFile) -> BasedResultOutput[ImageFileInfo]: ...

    @abstractmethod
    def update_filename(self, image_file: ImageFile, new_filename: str) -> BasedResultOutput[ImageFile]: ...

    @abstractmethod
    def validate_filename(self, filename: Optional[str]) -> BasedResultOutput[str]: ...

    @abstractmethod
    def sanitize_filename(self, filename: str) -> str: ...

    @abstractmethod
    def trim_filename(self, filename: str, *, max_length: int) -> BasedResultOutput[str]: ...
