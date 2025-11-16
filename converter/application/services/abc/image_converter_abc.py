from abc import ABC, abstractmethod

from PIL.ImageFile import ImageFile

from converter.application.commands.schemas.conversion import ConversionRequest
from common.core.result import ContextResult, as_awaitable_result


class ImageConverterABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aconvert(self, file: ImageFile, options: ConversionRequest.Options) -> ContextResult[ImageFile]: ...
