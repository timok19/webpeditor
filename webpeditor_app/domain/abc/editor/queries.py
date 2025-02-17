from abc import ABC, abstractmethod

from returns.maybe import Maybe

from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorImageAssetsQueriesABC(ABC):
    @abstractmethod
    async def get_original_asset_async(self, user_id: str) -> Maybe[EditorOriginalImageAsset]: ...

    @abstractmethod
    async def get_edited_asset_async(self, user_id: str) -> Maybe[EditorEditedImageAsset]: ...
