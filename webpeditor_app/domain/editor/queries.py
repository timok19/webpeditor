from returns.maybe import Some, Nothing, Maybe

from webpeditor_app.domain.abc.editor.queries import EditorQueriesABC
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


class EditorQueries(EditorQueriesABC):
    async def get_original_asset_async(self, user_id: str) -> Maybe[EditorOriginalImageAsset]:
        original_image_asset = await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()
        return Some(original_image_asset) if original_image_asset is not None else Nothing

    async def get_edited_asset_async(self, user_id: str) -> Maybe[EditorEditedImageAsset]:
        edited_image_asset = await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()
        return Some(edited_image_asset) if edited_image_asset is not None else Nothing
