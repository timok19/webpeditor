from typing import final

from expression import Option

from core.result import ContextResult, ErrorContext, as_awaitable_result
from infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from infrastructure.database.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


@final
class EditorRepository(EditorRepositoryABC):
    @as_awaitable_result
    async def aget_original_asset(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]:
        original_asset = await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(original_asset).to_result(
            ErrorContext.not_found(f"Unable to find Editor Original Image Asset for User '{user_id}'")
        )
        return ContextResult[EditorOriginalImageAsset].from_result(result)

    @as_awaitable_result
    async def aget_edited_asset(self, user_id: str) -> ContextResult[EditorEditedImageAsset]:
        edited_asset = await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(edited_asset).to_result(
            ErrorContext.not_found(f"Unable to find Editor Edited Image Asset for User '{user_id}'")
        )
        return ContextResult[EditorEditedImageAsset].from_result(result)
