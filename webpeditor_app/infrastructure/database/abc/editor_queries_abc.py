from abc import ABC, abstractmethod

from webpeditor_app.core.extensions.result_extensions import FutureContextResult
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorQueriesABC(ABC):
    @abstractmethod
    async def get_original_asset_async(self, user_id: str) -> FutureContextResult[EditorOriginalImageAsset]: ...

    @abstractmethod
    async def get_edited_asset_async(self, user_id: str) -> FutureContextResult[EditorEditedImageAsset]: ...
