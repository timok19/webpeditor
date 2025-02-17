from abc import ABC, abstractmethod

from returns.maybe import Maybe

from webpeditor_app.models.converter import ConverterImageAsset


class ConverterQueriesABC(ABC):
    @abstractmethod
    async def get_converted_asset_async(self, user_id: str) -> Maybe[ConverterImageAsset]: ...
