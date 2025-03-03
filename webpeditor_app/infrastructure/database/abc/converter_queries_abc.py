from abc import ABC, abstractmethod

from webpeditor_app.core.extensions.result_extensions import FutureContextResult
from webpeditor_app.models.converter import ConverterImageAsset


class ConverterQueriesABC(ABC):
    @abstractmethod
    async def get_converted_asset_async(self, user_id: str) -> FutureContextResult[ConverterImageAsset]: ...
