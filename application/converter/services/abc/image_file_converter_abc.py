from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from application.converter.commands.schemas.conversion import ConversionRequest
from core.result import ContextResult, as_awaitable_result


class ImageFileConverterABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aconvert(self, file: ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile]: ...
