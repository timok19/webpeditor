from abc import ABC, abstractmethod


from webpeditor_app.core.converter.models import ConversionResponse, ConversionRequest
from webpeditor_app.common.resultant import ResultantValue


class ImageConverterServiceABC(ABC):
    @abstractmethod
    def convert(self, request: ConversionRequest) -> ResultantValue[ConversionResponse]: ...
