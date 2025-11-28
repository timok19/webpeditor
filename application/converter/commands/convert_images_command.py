import asyncio
import hashlib
from typing import Annotated, Final, cast, final, Optional

from PIL import Image
from PIL.ImageFile import ImageFile
from aiocache.backends.memory import SimpleMemoryCache
from django.http import HttpRequest
from ninja import UploadedFile
from pydantic import HttpUrl
from types_linq import Enumerable

from application.common.abc.filename_service_abc import FilenameServiceABC
from application.common.abc.image_file_service_abc import ImageFileServiceABC
from application.common.abc.validator_abc import ValidatorABC
from application.common.services.session_service_factory import SessionServiceFactory
from core.types import Pair
from domain.common.models import ImageAssetFile
from domain.converter.models import ConverterConvertedImageAssetFile, ConverterOriginalImageAssetFile
from infrastructure.abc.files_repository_abc import FilesRepositoryABC
from application.common.services.models.file_info import ImageFileInfo
from infrastructure.repositories.converter_files.converter_files_repository import ConverterFilesRepository
from application.converter.commands.schemas.conversion import ConversionRequest, ConversionResponse
from application.converter.services.abc.image_file_converter_abc import ImageFileConverterABC
from core.abc.logger_abc import LoggerABC
from core.result import (
    ContextResult,
    EnumerableContextResult,
    as_awaitable_result,
    as_awaitable_enumerable_result,
)
from infrastructure.abc.converter_image_assets_repository_abc import ConverterImageAssetsRepositoryABC
from infrastructure.repositories.converter_files.models import UploadFileParams
from infrastructure.repositories.converter_image_assets.models import CreateAssetFileParams


@final
class ConvertImagesCommand:
    __CACHE: Final[SimpleMemoryCache] = SimpleMemoryCache()

    def __init__(
        self,
        session_service_factory: SessionServiceFactory,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        converter_files_repo: Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__],
        image_converter: ImageFileConverterABC,
        image_file_service: ImageFileServiceABC,
        filename_service: FilenameServiceABC,
        converter_repo: ConverterImageAssetsRepositoryABC,
        logger: LoggerABC,
    ) -> None:
        self.__session_service_factory: Final[SessionServiceFactory] = session_service_factory
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = conversion_request_validator
        self.__converter_files_repo: Final[Annotated[FilesRepositoryABC, ConverterFilesRepository.__name__]] = converter_files_repo
        self.__image_file_service: Final[ImageFileServiceABC] = image_file_service
        self.__filename_service: Final[FilenameServiceABC] = filename_service
        self.__image_converter: Final[ImageFileConverterABC] = image_converter
        self.__converter_repo: Final[ConverterImageAssetsRepositoryABC] = converter_repo
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_enumerable_result
    async def ahandle(
        self,
        http_request: HttpRequest,
        request: ConversionRequest,
    ) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__conversion_request_validator.validate(request)
            .abind(lambda _: self.__session_service_factory.create(http_request).aget_user_id())
            .abind_many(
                lambda user_id: self.__aget_cache(user_id, request).aif_empty(
                    self.__acleanup_previous_assets(user_id)
                    .abind(lambda _: self.__converter_repo.aget_or_create_asset(user_id))
                    .map(lambda _: (self.__aprocess(user_id, uploaded_file, request.options) for uploaded_file in request.files))
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
        user_id: str,
        uploaded_file: UploadedFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        with Image.open(uploaded_file) as image_file:
            return await (
                self.__image_file_service.verify_integrity(image_file)
                .bind(lambda file: self.__image_file_service.set_filename(file, uploaded_file.name))
                .abind(lambda file: self.__aget_original(user_id, file).amap2(self.__aconvert(user_id, file, options), self.__to_response))
            )

    @as_awaitable_result
    async def __aget_original(self, user_id: str, file: ImageFile) -> ContextResult[ConverterOriginalImageAssetFile]:
        return await (
            self.__image_file_service.get_info(file)
            .abind(lambda file_info: self.__aupload(user_id, "original", file_info).map(lambda url: (url, file_info)))
            .map(Pair[HttpUrl, ImageFileInfo].from_tuple)
            .abind(
                lambda pair: self.__converter_repo.aget_or_create_asset_file(
                    user_id,
                    params=CreateAssetFileParams(
                        file_url=str(pair.item1),
                        file_info=pair.item2,
                        file_type=ConverterOriginalImageAssetFile,
                    ),
                )
            )
        )

    @as_awaitable_result
    async def __aconvert(
        self,
        user_id: str,
        file: ImageFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConverterConvertedImageAssetFile]:
        return await (
            self.__image_converter.aconvert(file, options)
            .bind(self.__image_file_service.get_info)
            .abind(lambda file_info: self.__aupload(user_id, "converted", file_info).map(lambda url: (url, file_info)))
            .map(Pair[HttpUrl, ImageFileInfo].from_tuple)
            .abind(
                lambda pair: self.__converter_repo.aget_or_create_asset_file(
                    user_id,
                    params=CreateAssetFileParams(
                        file_url=str(pair.item1),
                        file_info=pair.item2,
                        file_type=ConverterConvertedImageAssetFile,
                    ),
                )
            )
        )

    @as_awaitable_result
    async def __aupload(self, user_id: str, relative_folder_path: str, file_info: ImageFileInfo) -> ContextResult[HttpUrl]:
        return await self.__converter_files_repo.aupload_file(
            user_id,
            params=UploadFileParams(
                content=file_info.file_details.content,
                basename=file_info.filename_details.basename,
                relative_folder_path=relative_folder_path,
            ),
        )

    def __to_response(
        self,
        original_asset_file: ConverterOriginalImageAssetFile,
        converted_asset_file: ConverterConvertedImageAssetFile,
    ) -> ConversionResponse:
        original_image_data = self.__to_image_data(original_asset_file)
        converted_image_data = self.__to_image_data(converted_asset_file)
        return ConversionResponse.create(original_image_data, converted_image_data)

    @staticmethod
    def __to_image_data(asset_file: ImageAssetFile) -> ConversionResponse.ImageData:
        return ConversionResponse.ImageData(
            id=asset_file.id,
            url=str(asset_file.file_url),
            filename=asset_file.filename,
            filename_shorter=asset_file.filename_shorter,
            content_type=asset_file.content_type,
            format=asset_file.format,
            format_description=asset_file.format_description,
            size=asset_file.size,
            width=asset_file.width,
            height=asset_file.height,
            aspect_ratio=asset_file.aspect_ratio,
            color_mode=asset_file.color_mode,
            exif_data=asset_file.exif_data,
        )

    @as_awaitable_enumerable_result
    async def __aget_cache(self, user_id: str, request: ConversionRequest) -> EnumerableContextResult[ConversionResponse]:
        results = await self.__CACHE.get(self.__get_cache_key(user_id, request))
        return cast(Optional[EnumerableContextResult[ConversionResponse]], results) or EnumerableContextResult[ConversionResponse].empty()

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
        Enumerable(request.files).select_many(lambda file: file.chunks()).as_more().for_each(hasher.update)
        return f"{user_id}-{request.options.quality}-{request.options.output_format}-{hasher.hexdigest()}"
