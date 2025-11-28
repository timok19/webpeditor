from abc import ABC, abstractmethod

from core.result import ContextResult, as_awaitable_result
from domain.common.models import ImageAssetFile
from domain.converter.models import ConverterImageAsset
from infrastructure.repositories.converter_image_assets.models import CreateAssetFileParams


class ConverterImageAssetsRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aget_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_or_create_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]: ...

    @abstractmethod
    @as_awaitable_result
    async def aasset_exists(self, user_id: str) -> ContextResult[bool]: ...

    @abstractmethod
    @as_awaitable_result
    async def adelete_asset(self, user_id: str) -> ContextResult[None]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_or_create_asset_file[T: ImageAssetFile](self, user_id: str, *, params: CreateAssetFileParams[T]) -> ContextResult[T]: ...
