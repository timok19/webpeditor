import asyncio
import hashlib
from decimal import Decimal
from typing import Annotated, Final, cast, final, Optional

from PIL import Image
from PIL.ImageFile import ImageFile
from aiocache.backends.memory import SimpleMemoryCache
from django.http import HttpRequest
from ninja import UploadedFile
from ninja_extra.context import RouteContext

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.abc.validator_abc import ValidatorABC
from application.common.services.session_service_factory import SessionServiceFactory
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from application.common.services.models.file_info import ImageFileInfo
from infrastructure.database.models.base import BaseImageAssetFile
from infrastructure.repositories.converter_files_repository import ConverterFilesRepository
from application.converter.commands.schemas.conversion import ConversionRequest, ConversionResponse
from application.converter.services.abc.image_converter_abc import ImageConverterABC
from core.abc.logger_abc import LoggerABC
from core.result import (
    ContextResult,
    EnumerableContextResult,
    as_awaitable_result,
    as_awaitable_enumerable_result,
)
from core.types import Pair
from infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from infrastructure.database.models.converter import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ConvertImagesCommand:
    __CACHE: Final[SimpleMemoryCache] = SimpleMemoryCache()

    def __init__(
        self,
        route_context_validator: ValidatorABC[RouteContext],
        http_request_validator: ValidatorABC[HttpRequest],
        session_service_factory: SessionServiceFactory,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        image_converter: ImageConverterABC,
        image_file_service: ImageFileServiceABC,
        filename_service: FilenameServiceABC,
        converter_repo: ConverterRepositoryABC,
        logger: LoggerABC,
    ) -> None:
        self.__route_context_validator: Final[ValidatorABC[RouteContext]] = route_context_validator
        self.__http_request_validator: Final[ValidatorABC[HttpRequest]] = http_request_validator
        self.__session_service_factory: Final[SessionServiceFactory] = session_service_factory
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = conversion_request_validator
        self.__converter_files_repo: Final[Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]] = converter_files_repo
        self.__image_file_service: Final[ImageFileServiceABC] = image_file_service
        self.__filename_service: Final[FilenameServiceABC] = filename_service
        self.__image_converter: Final[ImageConverterABC] = image_converter
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_enumerable_result
    async def ahandle(
        self,
        context: Optional[RouteContext],
        request: ConversionRequest,
    ) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__conversion_request_validator.validate(request)
            .bind(lambda _: self.__route_context_validator.validate(context))
            .bind(lambda ctx: self.__http_request_validator.validate(ctx.request))
            .abind(lambda http_request: self.__session_service_factory.create(http_request).aget_user_id())
            .abind_many(
                lambda user_id: self.__aget_cache(user_id, request).aif_empty(
                    self.__acleanup_previous_assets(user_id)
                    .abind(lambda _: self.__converter_repo.aget_or_create_asset(user_id))
                    .map(lambda asset: (self.__aprocess(uploaded_file, asset, request.options) for uploaded_file in request.files))
                    .amap(lambda results: asyncio.gather(*results))
                    .abind_many(lambda results: self.__set_cache(user_id, request, results))
                    .tap_either(
                        lambda values: self.__logger.info(f"Successfully converted {values.count()} image(s) for User '{user_id}'"),
                        lambda errors: self.__logger.error(f"Failed to convert images for User '{user_id}'"),
                    )
                )
            )
        )

    @as_awaitable_result
    async def __acleanup_previous_assets(self, user_id: str) -> ContextResult[None]:
        asset_exists_result = await self.__converter_repo.aasset_exists(user_id)

        if asset_exists_result.is_error():
            return ContextResult[None].failure(asset_exists_result.error)

        if asset_exists_result.ok is False:
            return ContextResult[None].success(None)

        results = await asyncio.gather(
            self.__converter_repo.adelete_asset(user_id),
            self.__converter_files_repo.adelete_files(user_id, "original"),
            self.__converter_files_repo.adelete_files(user_id, "converted"),
        )

        return (
            EnumerableContextResult[None]
            .from_results(results)
            .where(lambda result: result.is_error())
            .first2(ContextResult[None].success(None))
        )

    @as_awaitable_result
    async def __aprocess(
        self,
        uploaded_file: UploadedFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        with Image.open(uploaded_file) as image_file:
            return await (
                self.__image_file_service.set_filename(image_file, uploaded_file.name)
                .bind(self.__image_file_service.verify_integrity)
                .abind(lambda file: self.__aget_original(file, asset).amap2(self.__aconvert(file, asset, options), self.__to_response))
            )

    @as_awaitable_result
    async def __aget_original(self, file: ImageFile, asset: ConverterImageAsset) -> ContextResult[ConverterOriginalImageAssetFile]:
        return await (
            self.__image_file_service.get_info(file)
            .abind(lambda file_info: self.__aupload(asset.user_id, "original", file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterOriginalImageAssetFile, pair.item1, pair.item2, asset))
        )

    @as_awaitable_result
    async def __aconvert(
        self,
        file: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConverterConvertedImageAssetFile]:
        return await (
            self.__image_converter.aconvert(file, options)
            .bind(self.__image_file_service.get_info)
            .abind(lambda file_info: self.__aupload(asset.user_id, "converted", file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterConvertedImageAssetFile, pair.item1, pair.item2, asset))
        )

    @as_awaitable_result
    async def __aupload(self, user_id: str, relative_folder_path: str, file_info: ImageFileInfo) -> ContextResult[Pair[ImageFileInfo, str]]:
        return await self.__converter_files_repo.aupload_file(
            user_id,
            relative_folder_path,
            file_info.filename_details.basename,
            file_info.file_details.content,
        ).map(lambda file_url: Pair(file_info, str(file_url)))

    def __to_response(self, original: ConverterOriginalImageAssetFile, converted: ConverterConvertedImageAssetFile) -> ConversionResponse:
        return ConversionResponse.create(self.__to_image_data(original), self.__to_image_data(converted))

    @staticmethod
    def __to_image_data(asset_file: BaseImageAssetFile) -> ConversionResponse.ImageData:
        return ConversionResponse.ImageData(
            id=asset_file.id,
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

    @as_awaitable_enumerable_result
    async def __aget_cache(self, user_id: str, request: ConversionRequest) -> EnumerableContextResult[ConversionResponse]:
        results = cast(
            Optional[EnumerableContextResult[ConversionResponse]],
            await self.__CACHE.get(self.__get_cache_key(user_id, request)),
        )
        return results or EnumerableContextResult[ConversionResponse].empty()

    @as_awaitable_enumerable_result
    async def __set_cache(
        self,
        user_id: str,
        request: ConversionRequest,
        results: list[ContextResult[ConversionResponse]],
    ) -> EnumerableContextResult[ConversionResponse]:
        values = EnumerableContextResult[ConversionResponse].from_results(results)
        await self.__CACHE.set(self.__get_cache_key(user_id, request), values)
        return values

    @staticmethod
    def __get_cache_key(user_id: str, request: ConversionRequest) -> str:
        hasher = hashlib.sha256()

        for file in request.files:
            for chunk in file.chunks():
                hasher.update(chunk)

        return f"{user_id}-{request.options.quality}-{request.options.output_format}-{hasher.hexdigest()}"
