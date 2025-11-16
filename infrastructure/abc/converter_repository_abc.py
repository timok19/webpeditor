from abc import ABC, abstractmethod

from application.common.services.models.file_info import ImageFileInfo
from core.result import ContextResult, as_awaitable_result
from infrastructure.database.models.converter import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


class ConverterRepositoryABC(ABC):
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
    async def acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        file_url: str,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]: ...
