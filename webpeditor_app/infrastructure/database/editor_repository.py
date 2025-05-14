from typing import final
from expression import Option
from webpeditor_app.core.context_result import AwaitableContextResult, ContextResult, ErrorContext
from webpeditor_app.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from webpeditor_app.models.editor import EditorOriginalImageAsset, EditorEditedImageAsset


@final
class EditorRepository(EditorRepositoryABC):
    def aget_original_asset(self, user_id: str) -> AwaitableContextResult[EditorOriginalImageAsset]:
        async def aget_original_asset() -> ContextResult[EditorOriginalImageAsset]:
            return ContextResult[EditorOriginalImageAsset].from_result(
                Option.of_optional(await EditorOriginalImageAsset.objects.filter(user_id=user_id).afirst()).to_result(
                    ErrorContext.not_found(f"Unable to find Editor Original Image Asset for User '{user_id}'")
                )
            )

        return AwaitableContextResult(aget_original_asset())

    def aget_edited_asset(self, user_id: str) -> AwaitableContextResult[EditorEditedImageAsset]:
        async def aget_edited_asset() -> ContextResult[EditorEditedImageAsset]:
            return ContextResult[EditorEditedImageAsset].from_result(
                Option.of_optional(await EditorEditedImageAsset.objects.filter(user_id=user_id).afirst()).to_result(
                    ErrorContext.not_found(f"Unable to find Editor Edited Image Asset for User '{user_id}'")
                )
            )

        return AwaitableContextResult(aget_edited_asset())
