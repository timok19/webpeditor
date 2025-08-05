import asyncio
from typing import Final, final

from PIL import Image
from PIL.ImageFile import ImageFile
from types_linq import Enumerable

from webpeditor_app.application.common.session_service import SessionService
from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.common.abc.validator_abc import ValidatorABC
from webpeditor_app.application.common.image_file.models.file_info import ImageFileInfo
from webpeditor_app.application.converter.handlers.schemas.conversion import ConversionRequest, ConversionResponse
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import (
    ContextResult,
    EnumerableContextResult,
    as_awaitable_result,
    as_awaitable_enumerable_result,
)
from webpeditor_app.globals import Pair, Unit
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ImageConversionHandler:
    def __init__(
        self,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        cloudinary_service: CloudinaryServiceABC,
        converter_service: ImageConverterABC,
        image_file_utility: ImageFileUtilityABC,
        converter_repo: ConverterRepositoryABC,
        user_repo: UserRepositoryABC,
        logger: LoggerABC,
    ) -> None:
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = conversion_request_validator
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__converter_service: Final[ImageConverterABC] = converter_service
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__converter_repo: Final[ConverterRepositoryABC] = converter_repo
        self.__user_repo: Final[UserRepositoryABC] = user_repo
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
            self.__acleanup_previous_images(user_id)
            .abind(lambda _: self.__user_repo.aget(user_id))
            .abind(self.__converter_repo.aget_or_create_asset)
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
            .log_results(
                lambda values: self.__logger.log_info(f"Successfully converted {values.count()} image(s) for User '{user_id}'", depth=4),
                lambda errors: self.__logger.log_error(f"Failed to convert images for User '{user_id}'", depth=4),
            )
        )

    @as_awaitable_result
    async def __acleanup_previous_images(self, user_id: str) -> ContextResult[Unit]:
        return await self.__converter_repo.aasset_exists(user_id).aif_then_else(
            lambda exists: not exists,
            lambda _: ContextResult[Unit].asuccess(Unit()),
            lambda _: self.__converter_repo.adelete_asset(user_id).abind(
                lambda _: self.__cloudinary_service.adelete_folder_recursively(f"{user_id}/converter")
            ),
        )

    @as_awaitable_result
    async def __aconvert_and_save(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        return await (
            self.__image_file_utility.get_file_info(image)
            .abind(lambda file_info: self.__aupload_file(f"{asset.user.id}/converter/original", file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterOriginalImageAssetFile, pair.item1, pair.item2, asset))
        ).amap2(
            self.__converter_service.convert_image(image, options)
            .bind(self.__image_file_utility.get_file_info)
            .abind(lambda file_info: self.__aupload_file(f"{asset.user.id}/converter/converted", file_info))
            .abind(lambda pair: self.__converter_repo.acreate_asset_file(ConverterConvertedImageAssetFile, pair.item1, pair.item2, asset))
            .map2(self.__image_file_utility.close_file(image), lambda result, _: result),
            lambda original, converted: ConversionResponse(
                original_data=ConversionResponse.ImageData.from_asset_file(original),
                converted_data=ConversionResponse.ImageData.from_asset_file(converted),
            ),
        )

    @as_awaitable_result
    async def __aupload_file(self, path_to_upload: str, file_info: ImageFileInfo) -> ContextResult[Pair[ImageFileInfo, str]]:
        public_id = f"{path_to_upload}/{file_info.file_basename}"
        return await self.__cloudinary_service.aupload_file(public_id, file_info.file_content).map(
            lambda file_url: Pair[ImageFileInfo, str](item1=file_info, item2=file_url)
        )
