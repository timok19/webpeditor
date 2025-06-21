from typing import Final, final
from expression import Option
from webpeditor_app.application.common.image_file.schemas import ImageFileInfo
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, acontext_result
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
    ConverterConvertedImageAssetFile,
)


@final
class ConverterRepository(ConverterRepositoryABC):
    def __init__(self, logger: WebPEditorLoggerABC) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = logger

    @acontext_result
    async def aget_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        result = Option.of_optional(image_asset).to_result(
            ErrorContext.not_found(f"Unable to find Converter Image Asset for User '{user_id}'")
        )
        return ContextResult[ConverterImageAsset].from_result(result)

    @acontext_result
    async def aget_or_create_asset(self, user: AppUser) -> ContextResult[ConverterImageAsset]:
        try:
            asset, exists = await ConverterImageAsset.objects.aget_or_create(user=user)
            self.__logger.log_debug(
                f"Asset '{asset.id}' for user '{user.id}' {'already exists' if exists else 'has been created'}"
            )
            return ContextResult[ConverterImageAsset].success(asset)
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to create Converter Image Asset for User '{user.id}'")
            return ContextResult[ConverterImageAsset].failure(ErrorContext.bad_request())

    @acontext_result
    async def aasset_exists(self, user_id: str) -> ContextResult[bool]:
        try:
            return ContextResult[bool].success(await ConverterImageAsset.objects.filter(user_id=user_id).aexists())
        except Exception as exception:
            message = f"Failed to check if Converter Image Asset exists for User '{user_id}'"
            self.__logger.log_exception(exception, message)
            return ContextResult[bool].failure(ErrorContext.bad_request())

    @acontext_result
    async def adelete_asset(self, user_id: str) -> ContextResult[None]:
        try:
            _, deleted_per_model = await ConverterImageAsset.objects.filter(user_id=user_id).adelete()
            for model, count in deleted_per_model.items():
                self.__logger.log_debug(f"Deleted '{model}': {count} for User '{user_id}'")
            return ContextResult[None].success(None)
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to delete Converter Image Asset for User '{user_id}'")
            return ContextResult[None].failure(ErrorContext.bad_request())

    @acontext_result
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
            message = f"Failed to create Converter Original Image Asset File with filename '{file_info.filename}' for User '{asset.user.id}'"
            self.__logger.log_exception(exception, message)
            return ContextResult[T].failure(ErrorContext.bad_request())
