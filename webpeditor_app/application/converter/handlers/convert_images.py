import asyncio
from decimal import Decimal
from typing import Annotated, Final, final

from PIL import Image
from PIL.ImageFile import ImageFile
from types_linq import Enumerable

from webpeditor_app.common.abc.files_repository_abc import FilesRepositoryABC
from webpeditor_app.infrastructure.database.models.base import BaseImageAssetFile
from webpeditor_app.infrastructure.repositories.converter_files_repository import ConverterFilesRepository
from webpeditor_app.common.session.session_service import SessionService
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.common.image_file.models.file_info import ImageFileInfo
from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest, ConversionResponse
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import (
    ContextResult,
    EnumerableContextResult,
    as_awaitable_result,
    as_awaitable_enumerable_result,
)
from webpeditor_app.types import Pair
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ConvertImages:
    def __init__(
        self,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        converter_service: ImageConverterABC,
        image_file_utility: ImageFileUtilityABC,
        converter_repo: ConverterRepositoryABC,
        logger: LoggerABC,
    ) -> None:
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = conversion_request_validator
        self.__converter_files_repo: Final[Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]] = converter_files_repo
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__converter_service: Final[ImageConverterABC] = converter_service
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_enumerable_result
    async def ahandle(self, request: ConversionRequest, session_service: SessionService) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__conversion_request_validator.validate(request)
            .to_result()
            .abind(lambda _: session_service.asynchronize())
            .abind_many(lambda user_id: self.__aconvert_files(user_id, request))
        )

    @as_awaitable_enumerable_result
    async def __aconvert_files(
        self,
        user_id: str,
        request: ConversionRequest,
    ) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__converter_repo.aasset_exists(user_id)
            .abind(lambda asset_exists: self.__acleanup_previous_assets(asset_exists, user_id))
            .abind(lambda _: self.__converter_repo.aget_or_create_asset(user_id))
            .map(lambda asset: Pair(Enumerable(request.files), asset))
            .map(
                lambda pair: pair.item1.select(
                    lambda file: self.__image_file_utility.normalize_filename(file.name)
                    .bind(lambda normalized: self.__image_file_utility.update_filename(Image.open(file), normalized))
                    .abind(lambda image: self.__aprocess(image, pair.item2, request.options))
                ),
            )
            .amap(lambda results: asyncio.gather(*results))
            .bind_many(EnumerableContextResult[ConversionResponse].from_results)
            .tap_either(
                lambda values: self.__logger.info(f"Successfully converted {values.count()} image(s) for User '{user_id}'", depth=4),
                lambda errors: self.__logger.error(f"Failed to convert images for User '{user_id}'", depth=4),
            )
        )

    @as_awaitable_result
    async def __acleanup_previous_assets(self, asset_exists: bool, user_id: str) -> ContextResult[None]:
        return (
            await self.__converter_repo.adelete_asset(user_id).abind(lambda _: self.__converter_files_repo.acleanup(user_id))
            if asset_exists
            else ContextResult.empty_success()
        )

    @as_awaitable_result
    async def __aprocess(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        return await self.__aget_original_and_save(image, asset).amap2(self.__aconvert_and_save(image, asset, options), self.__to_response)

    @as_awaitable_result
    async def __aget_original_and_save(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
    ) -> ContextResult[ConverterOriginalImageAssetFile]:
        return await (
            self.__image_file_utility.get_file_info(image)
            .abind(lambda file_info: self.__aupload_original(asset.user_id, file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterOriginalImageAssetFile, pair.item1, pair.item2, asset))
        )

    @as_awaitable_result
    async def __aconvert_and_save(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConverterConvertedImageAssetFile]:
        return await (
            self.__converter_service.aconvert_image(image, options)
            .bind(self.__image_file_utility.get_file_info)
            .abind(lambda file_info: self.__aupload_converted(asset.user_id, file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterConvertedImageAssetFile, pair.item1, pair.item2, asset))
        )

    @as_awaitable_result
    async def __aupload_original(self, user_id: str, file_info: ImageFileInfo) -> ContextResult[Pair[ImageFileInfo, str]]:
        return (
            await self.__image_file_utility.get_basename(file_info.filename_details.fullname)
            .abind(lambda base: self.__converter_files_repo.aupload_file(user_id, f"original/{base}", file_info.file_details.content))
            .map(lambda file_url: Pair[ImageFileInfo, str](item1=file_info, item2=str(file_url)))
        )

    @as_awaitable_result
    async def __aupload_converted(self, user_id: str, file_info: ImageFileInfo) -> ContextResult[Pair[ImageFileInfo, str]]:
        return (
            await self.__image_file_utility.get_basename(file_info.filename_details.fullname)
            .abind(lambda base: self.__converter_files_repo.aupload_file(user_id, f"converted/{base}", file_info.file_details.content))
            .map(lambda file_url: Pair[ImageFileInfo, str](item1=file_info, item2=str(file_url)))
        )

    def __to_response(self, original: ConverterOriginalImageAssetFile, converted: ConverterConvertedImageAssetFile) -> ConversionResponse:
        original_image_data = self.__to_image_data(original)
        converted_image_data = self.__to_image_data(converted)
        return ConversionResponse.create(original_image_data, converted_image_data)

    @staticmethod
    def __to_image_data(asset_file: BaseImageAssetFile) -> ConversionResponse.ImageData:
        return ConversionResponse.ImageData(
            url=asset_file.file_url,
            filename=asset_file.filename,
            filename_shorter=asset_file.filename_shorter,
            content_type=asset_file.content_type,
            format=asset_file.format,
            format_description=asset_file.format_description,
            size=asset_file.size or 0,
            width=asset_file.width or 0,
            height=asset_file.height or 0,
            aspect_ratio=asset_file.aspect_ratio or Decimal(),
            color_mode=asset_file.color_mode,
            exif_data=asset_file.exif_data,
        )
