from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest
from webpeditor_app.core.result import ContextResult


class ImageConverterABC(ABC):
    @abstractmethod
    def convert_image(
        self,
        image: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile]: ...
