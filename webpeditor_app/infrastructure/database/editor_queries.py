from webpeditor_app.core.context_result import ContextResult, ErrorContext
from webpeditor_app.infrastructure.database.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorQueries(EditorQueriesABC):
    async def get_original_asset_async(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]:
        # TODO: optimize the same way as in converter_queries
        original_image_asset = await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()
        return (
            ContextResult[EditorOriginalImageAsset].Error2(
                ErrorContext.ErrorCode.NOT_FOUND,
                f"Unable to find Editor Original Image Asset for User '{user_id}'",
            )
            if original_image_asset is None
            else ContextResult[EditorOriginalImageAsset].Ok(original_image_asset)
        )

    async def get_edited_asset_async(self, user_id: str) -> ContextResult[EditorEditedImageAsset]:
        edited_image_asset = await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()
        return (
            ContextResult[EditorEditedImageAsset].Error2(
                ErrorContext.ErrorCode.NOT_FOUND,
                f"Unable to find Editor Edited Image Asset for User '{user_id}'",
            )
            if edited_image_asset is None
            else ContextResult[EditorEditedImageAsset].Ok(edited_image_asset)
        )
