from abc import ABC, abstractmethod
from typing import Collection

from webpeditor_app.common.result_extensions import ValueResult
from webpeditor_app.core.auth.session_service import SessionService
from webpeditor_app.core.converter.schemas.conversion import ConversionRequest, ConversionResponse
from webpeditor_app.core.converter.schemas.download import DownloadAllZipResponse


class ImageConverterABC(ABC):
    @abstractmethod
    async def convert_async(self, request: ConversionRequest, session_service: SessionService) -> Collection[ValueResult[ConversionResponse]]: ...

    @abstractmethod
    async def download_all_as_zip_async(self, session_service: SessionService) -> ValueResult[DownloadAllZipResponse]: ...
