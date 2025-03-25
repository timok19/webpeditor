from expression import Option
from webpeditor_app.core.context_result import ContextResult, ErrorContext
from webpeditor_app.infrastructure.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorQueries(EditorQueriesABC):
    async def get_original_asset_async(self, user_id: str) -> ContextResult[EditorOriginalImageAsset]:
        original_image_asset = await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()
        error_context = ErrorContext.not_found(f"Unable to find Editor Original Image Asset for User '{user_id}'")
        return ContextResult[EditorOriginalImageAsset].from_result(
            Option.of_optional(original_image_asset).to_result(error_context)
        )

    async def get_edited_asset_async(self, user_id: str) -> ContextResult[EditorEditedImageAsset]:
        edited_image_asset = await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()
        error_context = ErrorContext.not_found(f"Unable to find Editor Edited Image Asset for User '{user_id}'")
        return ContextResult[EditorEditedImageAsset].from_result(
            Option.of_optional(edited_image_asset).to_result(error_context)
        )
