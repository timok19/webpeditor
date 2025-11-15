from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from webpeditor_app.application.common.utilities.models.file_info import ImageFileInfo
from webpeditor_app.core.result import ContextResult


class ImageFileUtilityABC(ABC):
    @abstractmethod
    def get_info(self, file: ImageFile) -> ContextResult[ImageFileInfo]: ...

    @abstractmethod
    def update_filename(self, file: ImageFile, new_filename: str) -> ContextResult[ImageFile]: ...

    @abstractmethod
    def verify_integrity(self, file: ImageFile) -> ContextResult[ImageFile]: ...
