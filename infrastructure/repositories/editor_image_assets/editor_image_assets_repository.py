from typing import final

from expression import Option

from core.result import ContextResult, ErrorContext, as_awaitable_result
from infrastructure.abc.editor_image_assets_repository_abc import EditorImageAssetsRepositoryABC
from infrastructure.database.models.editor import EditorEditedImageAssetDo, EditorOriginalImageAssetDo


@final
class EditorImageAssetsRepository(EditorImageAssetsRepositoryABC):
    @as_awaitable_result
    async def aget_original_asset(self, user_id: str) -> ContextResult[EditorOriginalImageAssetDo]:
        original_asset = await EditorOriginalImageAssetDo.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(original_asset).to_result(
            ErrorContext.not_found(f"Unable to find Editor Original Image Asset for User '{user_id}'")
        )
        return ContextResult[EditorOriginalImageAssetDo].from_result(result)

    @as_awaitable_result
    async def aget_edited_asset(self, user_id: str) -> ContextResult[EditorEditedImageAssetDo]:
        edited_asset = await EditorEditedImageAssetDo.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(edited_asset).to_result(
            ErrorContext.not_found(f"Unable to find Editor Edited Image Asset for User '{user_id}'")
        )
        return ContextResult[EditorEditedImageAssetDo].from_result(result)
