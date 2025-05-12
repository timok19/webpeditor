from abc import ABC, abstractmethod

from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import ContextResult
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
    ConverterConvertedImageAssetFile,
)


class ConverterRepositoryABC(ABC):
    @abstractmethod
    async def get_asset_async(self, user_id: str) -> ContextResult[ConverterImageAsset]: ...

    @abstractmethod
    async def create_asset_async(self, user: AppUser) -> ContextResult[ConverterImageAsset]: ...

    @abstractmethod
    async def asset_exists_async(self, user_id: str) -> ContextResult[bool]: ...

    @abstractmethod
    async def delete_asset_async(self, user_id: str) -> ContextResult[None]: ...

    @abstractmethod
    async def create_asset_file_async[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]: ...
