from abc import ABC, abstractmethod

from webpeditor_app.core.context_result import AwaitableContextResult
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorRepositoryABC(ABC):
    @abstractmethod
    def aget_original_asset(self, user_id: str) -> AwaitableContextResult[EditorOriginalImageAsset]: ...

    @abstractmethod
    def aget_edited_asset(self, user_id: str) -> AwaitableContextResult[EditorEditedImageAsset]: ...
