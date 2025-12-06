from decimal import Decimal
from typing import Final, cast, final

from pydantic import HttpUrl

from application.common.services.models.file_info import ImageFileInfo
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext, as_awaitable_result
from core.types import Pair
from domain.common.models import ImageAssetFile
from domain.converter.models import ConverterConvertedImageAssetFile, ConverterImageAsset
from infrastructure.abc.converter_image_assets_repository_abc import ConverterImageAssetsRepositoryABC
from infrastructure.database.models.base import BaseImageAssetFileDo
from infrastructure.database.models.converter import (
    ConverterConvertedImageAssetFileDo,
    ConverterImageAssetDo,
    ConverterOriginalImageAssetFileDo,
)
from infrastructure.repositories.converter_image_assets.models import CreateAssetFileParams
from webpeditor import settings


@final
class ConverterImageAssetsRepository(ConverterImageAssetsRepositoryABC):
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aget_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        return await self.__aget_or_create_asset(user_id).map(self.__map_empty_asset_to_domain)

    @as_awaitable_result
    async def aget_or_create_asset(self, user_id: str) -> ContextResult[ConverterImageAsset]:
        try:
            asset_do, _ = await ConverterImageAssetDo.objects.aget_or_create(user_id=user_id)
            return ContextResult[ConverterImageAsset].success(self.__map_empty_asset_to_domain(asset_do))
        except Exception as exception:
            self.__logger.exception(exception, f"Failed to get or create Converter Image Asset for User '{user_id}'")
            return ContextResult[ConverterImageAsset].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def aasset_exists(self, user_id: str) -> ContextResult[bool]:
        try:
            return ContextResult[bool].success(await ConverterImageAssetDo.objects.filter(user_id=user_id).aexists())
        except Exception as exception:
            message = f"Failed to check if Converter Image Asset exists for User '{user_id}'"
            self.__logger.exception(exception, message)
            return ContextResult[bool].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def adelete_asset(self, user_id: str) -> ContextResult[None]:
        try:
            asset_do = await ConverterImageAssetDo.objects.filter(user_id=user_id).afirst()
            if asset_do is None:
                return ContextResult[None].failure(ErrorContext.not_found(f"Converter Image Asset for User '{user_id}' not found"))

            deleted_original = await ConverterOriginalImageAssetFileDo.objects.filter(image_asset=asset_do).adelete()
            deleted_converted = await ConverterConvertedImageAssetFileDo.objects.filter(image_asset=asset_do).adelete()

            if settings.IS_DEVELOPMENT:
                for model, count in {
                    **Pair[int, dict[str, int]].from_tuple(deleted_original).item2,
                    **Pair[int, dict[str, int]].from_tuple(deleted_converted).item2,
                }.items():
                    self.__logger.debug(f"Deleted '{model}': {count} for User '{user_id}'")

            return ContextResult[None].success(None)
        except Exception as exception:
            self.__logger.exception(exception, f"Unable to delete Converter Image Asset for User '{user_id}'")
            return ContextResult[None].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def aget_or_create_asset_file[T: ImageAssetFile](self, user_id: str, *, params: CreateAssetFileParams[T]) -> ContextResult[T]:
        asset_file_type = self.__map_file_type(params.file_type)
        return await (
            self.__aget_or_create_asset(user_id)
            .abind(lambda asset: self.__aget_or_create_asset_file(asset_file_type, params.file_info, params.file_url, asset))
            .map(self.__map_asset_file_to_domain)
            .map(lambda asset_file: cast(T, asset_file))
        )

    @as_awaitable_result
    async def __aget_or_create_asset(self, user_id: str) -> ContextResult[ConverterImageAssetDo]:
        try:
            asset_do, _ = await ConverterImageAssetDo.objects.aget_or_create(user_id=user_id)
            return ContextResult[ConverterImageAssetDo].success(asset_do)
        except Exception as exception:
            message = f"Unable to get or create Converter Image Asset for User '{user_id}'"
            self.__logger.exception(exception, message)
            return ContextResult[ConverterImageAssetDo].failure(ErrorContext.bad_request())

    @as_awaitable_result
    async def __aget_or_create_asset_file[T: BaseImageAssetFileDo](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        file_url: str,
        asset: ConverterImageAssetDo,
    ) -> ContextResult[T]:
        try:
            value, _ = await asset_file_type.objects.aget_or_create(
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
            return ContextResult[T].success(value)
        except Exception as exception:
            message = (
                f"Failed to create '{asset_file_type.__name__}' with filename "
                f"'{file_info.filename_details.fullname}' for User '{asset.user_id}' with {ConverterImageAssetDo.__name__} '{asset.id}'"
            )
            self.__logger.exception(exception, message)
            return ContextResult[T].failure(ErrorContext.bad_request())

    @staticmethod
    def __map_file_type[T: ImageAssetFile](file_type: type[T]) -> type[BaseImageAssetFileDo]:
        return ConverterConvertedImageAssetFileDo if file_type is ConverterConvertedImageAssetFile else ConverterOriginalImageAssetFileDo

    @staticmethod
    def __map_empty_asset_to_domain(asset_do: ConverterImageAssetDo) -> ConverterImageAsset:
        return ConverterImageAsset.create_empty(asset_do.id, asset_do.user_id, asset_do.created_at)

    @staticmethod
    def __map_asset_file_to_domain(asset_file_do: BaseImageAssetFileDo) -> ImageAssetFile:
        return ImageAssetFile(
            id=asset_file_do.id,
            file_url=HttpUrl(asset_file_do.file_url),
            filename=asset_file_do.filename,
            filename_shorter=asset_file_do.filename_shorter,
            content_type=asset_file_do.content_type,
            format=asset_file_do.format,
            format_description=asset_file_do.format_description,
            size=asset_file_do.size or 0,
            width=asset_file_do.width or 0,
            height=asset_file_do.height or 0,
            aspect_ratio=asset_file_do.aspect_ratio or Decimal(),
            color_mode=asset_file_do.color_mode,
            exif_data=asset_file_do.exif_data,
        )
