from typing import final
from expression import Option
from webpeditor_app.core.result import ContextResult, ErrorContext, acontext_result
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


@final
class EditorRepository(EditorRepositoryABC):
    @acontext_result
    async def aget_original_asset(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]:
        original_asset = await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(original_asset).to_result(
            ErrorContext.not_found(f"Unable to find Editor Original Image Asset for User '{user_id}'")
        )
        return ContextResult[EditorOriginalImageAsset].from_result(result)

    @acontext_result
    async def aget_edited_asset(self, user_id: str) -> ContextResult[EditorEditedImageAsset]:
        edited_asset = await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(edited_asset).to_result(
            ErrorContext.not_found(f"Unable to find Editor Edited Image Asset for User '{user_id}'")
        )
        return ContextResult[EditorEditedImageAsset].from_result(result)
