from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from webpeditor_app.application.converter.schemas.conversion import ConversionRequest
from webpeditor_app.core.context_result import ContextResult


class ConverterServiceABC(ABC):
    @abstractmethod
    def convert_image(
        self,
        image: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ImageFile]: ...
