from typing import Final, final

from expression import Option

from webpeditor_app.application.common.image_file.models import ImageFileInfo
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, as_awaitable_result
from webpeditor_app.globals import Unit
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.database.models import AppUser
from webpeditor_app.infrastructure.database.models import (
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
        image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(image_asset).to_result(
            ErrorContext.not_found(f"Unable to find Converter Image Asset for User '{user_id}'")
        )
        return ContextResult[ConverterImageAsset].from_result(result)

    @as_awaitable_result
    async def aget_or_create_asset(self, user: AppUser) -> ContextResult[ConverterImageAsset]:
        try:
            asset, _ = await ConverterImageAsset.objects.aget_or_create(user=user)
            self.__logger.log_debug(f"Asset '{asset.id}' for User '{user.id}' has been created")
            return ContextResult[ConverterImageAsset].success(asset)
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to create Converter Image Asset for User '{user.id}'")
            return ContextResult[ConverterImageAsset].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def aasset_exists(self, user_id: str) -> ContextResult[bool]:
        try:
            return ContextResult[bool].success(await ConverterImageAsset.objects.filter(user_id=user_id).aexists())
        except Exception as exception:
            message = f"Failed to check if Converter Image Asset exists for User '{user_id}'"
            self.__logger.log_exception(exception, message)
            return ContextResult[bool].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def adelete_asset(self, user_id: str) -> ContextResult[Unit]:
        try:
            number_of_deleted, deleted_per_model = await ConverterImageAsset.objects.filter(user_id=user_id).adelete()
            self.__logger.log_info(f"Deleted {number_of_deleted} Converter Image Assets related records for User '{user_id}'")

            for model, count in deleted_per_model.items():
                self.__logger.log_debug(f"Deleted '{model}': {count} for User '{user_id}'")

            return ContextResult[Unit].success(Unit())
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to delete Converter Image Asset for User '{user_id}'")
            return ContextResult[Unit].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        file_url: str,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]:
        try:
            asset_file = await asset_file_type.objects.acreate(
                file_url=file_url,
                filename=file_info.filename,
                filename_shorter=file_info.filename_shorter,
                content_type=f"image/{file_info.file_format.lower()}",
                format=file_info.file_format,
                format_description=file_info.file_format_description or "",
                size=file_info.size,
                width=file_info.width,
                height=file_info.height,
                aspect_ratio=file_info.aspect_ratio,
                color_mode=file_info.color_mode,
                exif_data=file_info.exif_data,
                image_asset=asset,
            )
            return ContextResult[T].success(asset_file)
        except Exception as exception:
            message = (
                f"Failed to create Converter Original Image Asset File with filename '{file_info.filename}' for User '{asset.user.id}'"
            )
            self.__logger.log_exception(exception, message)
            return ContextResult[T].failure(ErrorContext.bad_request())
