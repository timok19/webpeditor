from returns.maybe import Maybe, Nothing, Some

from webpeditor_app.domain.abc.converter.queries import ConverterImageAssetQueriesABC
from webpeditor_app.models.converter import ConverterImageAsset


class ConverterImageAssetQueries(ConverterImageAssetQueriesABC):
    async def get_converted_asset_async(self, user_id: str) -> Maybe[ConverterImageAsset]:
        converted_image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        return Some(converted_image_asset) if converted_image_asset is not None else Nothing
