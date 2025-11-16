from typing import Final, final

from expression import Option

from webpeditor import settings
from common.application.utilities.models.file_info import ImageFileInfo
from common.core.abc.logger_abc import LoggerABC
from common.core.result import ContextResult, ErrorContext, as_awaitable_result
from converter.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from converter.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ConverterRepository(ConverterRepositoryABC):
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aget_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(asset).to_result(ErrorContext.not_found(f"Unable to find Converter Image Asset for User '{user_id}'"))
        return ContextResult[ConverterImageAsset].from_result(result)

    @as_awaitable_result
    async def aget_or_create_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        try:
            asset, _ = await ConverterImageAsset.objects.aget_or_create(user_id=user_id)
            return ContextResult[ConverterImageAsset].success(asset)
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to get or create Converter Image Asset for User '{user_id}'")
            return ContextResult[ConverterImageAsset].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def aasset_exists(self, user_id: str) -> ContextResult[bool]:
        try:
            return ContextResult[bool].success(await ConverterImageAsset.objects.filter(user_id=user_id).aexists())
        except Exception as exception:
            message = f"Failed to check if Converter Image Asset exists for User '{user_id}'"
            self.__logger.exception(exception, message)
            return ContextResult[bool].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def adelete_asset(self, user_id: str) -> ContextResult[None]:
        try:
            _, deleted_per_model = await ConverterImageAsset.objects.filter(user_id=user_id).adelete()
            if settings.IS_DEVELOPMENT:
                for model, count in deleted_per_model.items():
                    self.__logger.debug(f"Deleted '{model}': {count} for User '{user_id}'")
            return ContextResult[None].success(None)
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to delete Converter Image Asset for User '{user_id}'")
            return ContextResult[None].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        file_url: str,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]:
        try:
            return ContextResult[T].success(
                await asset_file_type.objects.acreate(
                    file_url=file_url,
                    filename=file_info.filename_details.fullname,
                    filename_shorter=file_info.filename_details.short,
                    content_type=f"image/{file_info.file_details.format.lower()}",
                    format=file_info.file_details.format,
                    format_description=file_info.file_details.format_description or "",
                    size=file_info.file_details.size,
                    width=file_info.file_details.width,
                    height=file_info.file_details.height,
                    aspect_ratio=file_info.file_details.aspect_ratio,
                    color_mode=file_info.file_details.color_mode,
                    exif_data=file_info.file_details.exif_data,
                    image_asset=asset,
                )
            )
        except Exception as exception:
            message = f"Failed to create '{T.__name__}' with filename '{file_info.filename_details.fullname}' for User '{asset.user_id}'"
            self.__logger.exception(exception, message)
            return ContextResult[T].failure(ErrorContext.bad_request())
