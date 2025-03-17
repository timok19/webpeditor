from webpeditor_app.core.context_result import ContextResult, ErrorContext
from webpeditor_app.infrastructure.database.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.models.converter import ConverterImageAsset


class ConverterQueries(ConverterQueriesABC):
    async def get_converted_asset_async(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        converter_image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        return (
            ContextResult[ConverterImageAsset].Error2(
                ErrorContext.ErrorCode.NOT_FOUND,
                f"Unable to find Converter Image Asset for User '{user_id}'",
            )
            if converter_image_asset is None
            else ContextResult[ConverterImageAsset].Ok(converter_image_asset)
        )
