from abc import ABC, abstractmethod

from webpeditor_app.core.context_result import ContextResult
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorRepositoryABC(ABC):
    @abstractmethod
    async def get_original_asset_async(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]: ...

    @abstractmethod
    async def get_edited_asset_async(self, user_id: str) -> ContextResult[EditorEditedImageAsset]: ...
