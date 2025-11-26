from datetime import datetime
from typing import Optional, Self
from uuid import UUID

from domain.common.models import ImageAsset, ImageAssetFile


class ConverterOriginalImageAssetFile(ImageAssetFile): ...


class ConverterConvertedImageAssetFile(ImageAssetFile): ...


class ConverterImageAsset(ImageAsset):
    original_asset_file: Optional[ConverterOriginalImageAssetFile]
    converted_asset_file: Optional[ConverterConvertedImageAssetFile]

    @classmethod
    def create_empty(cls, id_: UUID, user_id: str, created_at: datetime) -> Self:
        return cls(id=id_, user_id=user_id, created_at=created_at, original_asset_file=None, converted_asset_file=None)
