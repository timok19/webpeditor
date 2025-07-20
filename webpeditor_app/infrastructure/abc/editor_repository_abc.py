from abc import ABC, abstractmethod

from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.infrastructure.database.models import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aget_original_asset(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_edited_asset(self, user_id: str) -> ContextResult[EditorEditedImageAsset]: ...
