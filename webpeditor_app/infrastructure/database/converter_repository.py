from typing import Final, final
from expression import Option
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import AwaitableContextResult, ContextResult, ErrorContext
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

    def aget_asset(self, user_id: str) -> AwaitableContextResult[ConverterImageAsset]:
        async def aget_asset() -> ContextResult[ConverterImageAsset]:
            optional_image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
            message = f"Unable to find Converter Image Asset for User '{user_id}'"
            result = Option.of_optional(optional_image_asset).to_result(ErrorContext.not_found(message))
            return ContextResult[ConverterImageAsset].from_result(result)

        return AwaitableContextResult(aget_asset())

    def acreate_asset(self, user: AppUser) -> AwaitableContextResult[ConverterImageAsset]:
        async def acreate_asset() -> ContextResult[ConverterImageAsset]:
            try:
                asset = await ConverterImageAsset.objects.acreate(user=user)
                return ContextResult[ConverterImageAsset].success(asset)
            except Exception as exception:
                self.__logger.log_exception(exception, f"Failed to create Converter Image Asset for User '{user.id}'")
                return ContextResult[ConverterImageAsset].failure(ErrorContext.server_error())

        return AwaitableContextResult(acreate_asset())

    def aasset_exists(self, user_id: str) -> AwaitableContextResult[bool]:
        async def aasset_exists() -> ContextResult[bool]:
            try:
                return ContextResult[bool].success(await ConverterImageAsset.objects.filter(user_id=user_id).aexists())
            except Exception as exception:
                message = f"Failed to check if Converter Image Asset exists for User '{user_id}'"
                self.__logger.log_exception(exception, message)
                return ContextResult[bool].failure(ErrorContext.server_error())

        return AwaitableContextResult(aasset_exists())

    def adelete_asset(self, user_id: str) -> AwaitableContextResult[None]:
        async def adelete_asset() -> ContextResult[None]:
            try:
                await ConverterImageAsset.objects.filter(user_id=user_id).adelete()
                return ContextResult[None].success(None)
            except Exception as exception:
                message = f"Failed to delete Converter Image Asset for User '{user_id}'"
                self.__logger.log_exception(exception, message)
                return ContextResult[None].failure(ErrorContext.server_error())

        return AwaitableContextResult(adelete_asset())

    def acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        asset: ConverterImageAsset,
    ) -> AwaitableContextResult[T]:
        async def acreate_asset_file() -> ContextResult[T]:
            try:
                asset_file = await asset_file_type.objects.acreate(
                    file=file_info.content_file,
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
                return ContextResult[T].failure(ErrorContext.server_error())

        return AwaitableContextResult(acreate_asset_file())
