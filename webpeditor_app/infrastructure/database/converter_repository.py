from typing import Final, final
from expression import Option
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import ContextResult, ErrorContext
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

    async def get_asset_async(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        optional_image_asset = await ConverterImageAsset.objects.filter(user_id=user_id).afirst()
        message = f"Unable to find Converter Image Asset for User '{user_id}'"
        result = Option.of_optional(optional_image_asset).to_result(ErrorContext.not_found(message))
        return ContextResult[ConverterImageAsset].from_result(result)

    async def create_asset_async(self, user: AppUser) -> ContextResult[ConverterImageAsset]:
        try:
            asset = await ConverterImageAsset.objects.acreate(user=user)
            return ContextResult[ConverterImageAsset].success(asset)
        except Exception as exception:
            self.__logger.log_exception(exception, f"Failed to create Converter Image Asset for User '{user.id}'")
            return ContextResult[ConverterImageAsset].failure(ErrorContext.server_error())

    async def asset_exists_async(self, user_id: str) -> ContextResult[bool]:
        try:
            return ContextResult[bool].success(await ConverterImageAsset.objects.filter(user_id=user_id).aexists())
        except Exception as exception:
            message = f"Failed to check if Converter Image Asset exists for User '{user_id}'"
            self.__logger.log_exception(exception, message)
            return ContextResult[bool].failure(ErrorContext.server_error())

    async def delete_asset_async(self, user_id: str) -> ContextResult[None]:
        try:
            await ConverterImageAsset.objects.filter(user_id=user_id).adelete()
            return ContextResult[None].success(None)
        except Exception as exception:
            message = f"Failed to delete Converter Image Asset for User '{user_id}'"
            self.__logger.log_exception(exception, message)
            return ContextResult[None].failure(ErrorContext.server_error())

    async def create_asset_file_async[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]:
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
            self.__logger.log_exception(
                exception,
                (
                    "Failed to create Converter Original Image Asset File "
                    + f"with filename '{file_info.filename}' "
                    + f"for User '{asset.user.id}'"
                ),
            )
            return ContextResult[T].failure(ErrorContext.server_error())
