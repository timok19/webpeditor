from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.types import Unit
from webpeditor_app.infrastructure.database.models import AppUser
from webpeditor_app.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)

if TYPE_CHECKING:
    from webpeditor_app.application.common.image_file.models import ImageFileInfo


class ConverterRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aget_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_or_create_asset(self, user: AppUser) -> ContextResult[ConverterImageAsset]: ...

    @abstractmethod
    @as_awaitable_result
    async def aasset_exists(self, user_id: str) -> ContextResult[bool]: ...

    @abstractmethod
    @as_awaitable_result
    async def adelete_asset(self, user_id: str) -> ContextResult[Unit]: ...

    @abstractmethod
    @as_awaitable_result
    async def acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: "ImageFileInfo",
        file_url: str,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]: ...
