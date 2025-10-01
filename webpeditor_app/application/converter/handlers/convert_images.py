import asyncio
from typing import Annotated, Callable, Final, final, Awaitable

from PIL import Image
from PIL.ImageFile import ImageFile
from types_linq import Enumerable

from webpeditor_app.common.abc.files_repository_abc import FilesRepositoryABC
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
from webpeditor_app.types import Pair, Unit
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
            .abind(self.__delete_asset_and_files_if_exists(user_id))
            .abind(lambda _: self.__converter_repo.aget_or_create_asset(user_id))
            .map(lambda asset: Pair(Enumerable(request.files), asset))
            .map(
                lambda pair: pair.item1.select(
                    lambda file: self.__image_file_utility.normalize_filename(file.name)
                    .bind(lambda normalized: self.__image_file_utility.update_filename(Image.open(file), normalized))
                    .abind(lambda updated_image: self.__aconvert_and_save(updated_image, pair.item2, request.options))
                ),
            )
            .amap(lambda results: asyncio.gather(*results))
            .bind_many(EnumerableContextResult[ConversionResponse].from_results)
            .tap_either(
                lambda values: self.__logger.info(f"Successfully converted {values.count()} image(s) for User '{user_id}'", depth=4),
                lambda errors: self.__logger.error(f"Failed to convert images for User '{user_id}'", depth=4),
            )
        )

    def __delete_asset_and_files_if_exists(self, user_id: str) -> Callable[[bool], Awaitable[ContextResult[Unit]]]:
        @as_awaitable_result
        async def cleanup(asset_exists: bool) -> ContextResult[Unit]:
            return (
                await self.__converter_repo.adelete_asset(user_id).abind(lambda _: self.__converter_files_repo.acleanup(user_id))
                if asset_exists
                else ContextResult[Unit].success(Unit())
            )

        return cleanup

    @as_awaitable_result
    async def __aconvert_and_save(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        return await (
            self.__image_file_utility.get_file_info(image)
            .abind(lambda file_info: self.__aupload_original(asset.user_id, file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterOriginalImageAssetFile, pair.item1, pair.item2, asset))
        ).amap2(
            self.__converter_service.convert_image(image, options)
            .bind(self.__image_file_utility.get_file_info)
            .abind(lambda file_info: self.__aupload_converted(asset.user_id, file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterConvertedImageAssetFile, pair.item1, pair.item2, asset))
            .map2(self.__image_file_utility.close_image(image), lambda result, _: result),
            lambda original, converted: ConversionResponse.create(
                ConversionResponse.ImageData.from_asset(original),
                ConversionResponse.ImageData.from_asset(converted),
            ),
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
