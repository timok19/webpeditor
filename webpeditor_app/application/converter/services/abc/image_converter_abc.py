from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest
from webpeditor_app.core.result import ContextResult, as_awaitable_result


class ImageConverterABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aconvert(self, file: ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile]: ...
