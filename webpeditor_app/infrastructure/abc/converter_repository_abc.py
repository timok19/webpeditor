from abc import ABC, abstractmethod

from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.context_result import AwaitableContextResult
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
    ConverterConvertedImageAssetFile,
)


class ConverterRepositoryABC(ABC):
    @abstractmethod
    def aget_asset(self, user_id: str) -> AwaitableContextResult[ConverterImageAsset]: ...

    @abstractmethod
    def acreate_asset(self, user: AppUser) -> AwaitableContextResult[ConverterImageAsset]: ...

    @abstractmethod
    def aasset_exists(self, user_id: str) -> AwaitableContextResult[bool]: ...

    @abstractmethod
    def adelete_asset(self, user_id: str) -> AwaitableContextResult[None]: ...

    @abstractmethod
    def acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        asset: ConverterImageAsset,
    ) -> AwaitableContextResult[T]: ...
