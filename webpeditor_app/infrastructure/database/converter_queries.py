from dataclasses import dataclass
from typing import final
from expression import Option
from webpeditor_app.core.context_result import ContextResult, ErrorContext
from webpeditor_app.infrastructure.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.models.converter import ConverterImageAsset


@final
@dataclass
class ConverterQueries(ConverterQueriesABC):
    async def get_converted_asset_async(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        optional_image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        error_context = ErrorContext.not_found(f"Unable to find Converter Image Asset for User '{user_id}'")
        return ContextResult[ConverterImageAsset].from_result(
            Option.of_optional(optional_image_asset).to_result(error_context)
        )
