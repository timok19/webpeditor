from abc import ABC, abstractmethod

from core.result import ContextResult, as_awaitable_result
from infrastructure.database.models.editor import EditorEditedImageAssetDo, EditorOriginalImageAssetDo


class EditorImageAssetsRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aget_original_asset(self, user_id: str) -> ContextResult[EditorOriginalImageAssetDo]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_edited_asset(self, user_id: str) -> ContextResult[EditorEditedImageAssetDo]: ...
