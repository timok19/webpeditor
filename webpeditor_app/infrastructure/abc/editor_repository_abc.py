from abc import ABC, abstractmethod

from webpeditor_app.core.context_result import ContextResult, acontext_result
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorRepositoryABC(ABC):
    @abstractmethod
    @acontext_result
    async def aget_original_asset(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]: ...

    @abstractmethod
    @acontext_result
    async def aget_edited_asset(self, user_id: str) -> ContextResult[EditorEditedImageAsset]: ...
