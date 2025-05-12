from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import ContextResult


class ConverterServiceABC(ABC):
    @abstractmethod
    def get_info(self, image: ImageFile) -> ContextResult[ImageFileInfo]: ...

    @abstractmethod
    def convert_image(
        self,
        image: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFileInfo]: ...
