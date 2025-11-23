from abc import ABC, abstractmethod
from typing import Union

from PIL import ImageFile

from application.common.services.models.file_info import ImageFileInfo
from core.result import ContextResult


class ImageFileServiceABC(ABC):
    @abstractmethod
    def verify_integrity(self, file: ImageFile.ImageFile) -> ContextResult[ImageFile.ImageFile]: ...

    @abstractmethod
    def get_info(self, file: ImageFile.ImageFile) -> ContextResult[ImageFileInfo]: ...

    @abstractmethod
    def set_filename(self, file: ImageFile.ImageFile, filename: Union[str, bytes]) -> ContextResult[ImageFile.ImageFile]: ...
