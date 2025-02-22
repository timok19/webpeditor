from returns.maybe import Maybe, Nothing, Some

from webpeditor_app.domain.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.models.converter import ConverterImageAsset


class ConverterQueries(ConverterQueriesABC):
    async def get_converted_asset_async(self, user_id: str) -> Maybe[ConverterImageAsset]:
        converted_image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        return Some(converted_image_asset) if converted_image_asset is not None else Nothing
