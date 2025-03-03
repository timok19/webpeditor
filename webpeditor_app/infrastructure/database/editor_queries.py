from webpeditor_app.core.extensions.result_extensions import FailureContext, FutureContextResult, ResultExtensions
from webpeditor_app.infrastructure.database.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorQueries(EditorQueriesABC):
    async def get_original_asset_async(self, user_id: str) -> FutureContextResult[EditorOriginalImageAsset]:
        original_image_asset = await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()
        return (
            ResultExtensions.future_failure(
                FailureContext.ErrorCode.NOT_FOUND,
                f"Unable to find Editor Original Image Asset for User '{user_id}'",
            )
            if original_image_asset is None
            else ResultExtensions.future_success(original_image_asset)
        )

    async def get_edited_asset_async(self, user_id: str) -> FutureContextResult[EditorEditedImageAsset]:
        edited_image_asset = await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()
        return (
            ResultExtensions.future_failure(
                FailureContext.ErrorCode.NOT_FOUND,
                f"Unable to find Editor Edited Image Asset for User '{user_id}'",
            )
            if edited_image_asset is None
            else ResultExtensions.future_success(edited_image_asset)
        )
