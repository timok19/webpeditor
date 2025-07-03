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
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import (
    ContextResult,
    EnumerableContextResult,
    acontext_result,
    aenumerable_context_result,
)
from webpeditor_app.globals import Unit
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ConvertImagesHandler:
    def __init__(
        self,
        conversion_request_validator: ValidatorABC[ConversionRequest],
        cloudinary_service: CloudinaryServiceABC,
        converter_service: ImageConverterABC,
        image_file_utility: ImageFileUtilityABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
        logger: WebPEditorLoggerABC,
    ) -> None:
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = conversion_request_validator
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__converter_service: Final[ImageConverterABC] = converter_service
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__converter_repository: Final[ConverterRepositoryABC] = converter_repository
        self.__user_repository: Final[UserRepositoryABC] = user_repository
        self.__logger: Final[WebPEditorLoggerABC] = logger

    @aenumerable_context_result
    async def ahandle(self, request: ConversionRequest, session_service: SessionService) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__conversion_request_validator.validate(request)
            .to_context_result()
            .abind(lambda _: session_service.asynchronize())
            .abind_many(lambda user_id: self.__aconvert_files(user_id, request))
        )

    @aenumerable_context_result
    async def __aconvert_files(
        self,
        user_id: str,
        request: ConversionRequest,
    ) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__acleanup_previous_images(user_id)
            .abind(lambda _: self.__user_repository.aget(user_id))
            .abind(self.__converter_repository.aget_or_create_asset)
            .map(lambda asset: (Enumerable(request.files), asset))
            .map(
                lambda files_asset_pair: files_asset_pair[0].select(
                    lambda file: self.__image_file_utility.normalize_filename(file.name)
                    .bind(lambda normalized: self.__image_file_utility.update_filename(Image.open(file), normalized))
                    .abind(lambda updated_image: self.__aconvert_and_save(updated_image, files_asset_pair[1], request.options))
                ),
            )
            .amap(lambda results: asyncio.gather(*results))
            .bind_many(EnumerableContextResult[ConversionResponse].from_results)
            .log_results(
                lambda values: self.__logger.log_info(f"Successfully converted {values.count()} image(s) for User '{user_id}'", depth=4),
                lambda errors: self.__logger.log_error(f"Failed to convert images for User '{user_id}'", depth=4),
            )
        )

    @acontext_result
    async def __acleanup_previous_images(self, user_id: str) -> ContextResult[Unit]:
        return await self.__converter_repository.aasset_exists(user_id).aif_then_else(
            lambda exists: not exists,
            lambda _: ContextResult[Unit].asuccess(Unit()),
            lambda _: self.__converter_repository.adelete_asset(user_id).abind(
                lambda _: self.__cloudinary_service.adelete_folder_recursively(f"{user_id}/converter")
            ),
        )

    @acontext_result
    async def __aconvert_and_save(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        return await (
            self.__image_file_utility.get_file_info(image)
            .abind(lambda file_info: self.__aupload_file(f"{asset.user.id}/converter/original", file_info))
            .abind(lambda info_url_pair: self.__acreate_asset_file(ConverterOriginalImageAssetFile, *info_url_pair, asset))
        ).amap2(
            self.__converter_service.convert_image(image, options)
            .bind(self.__image_file_utility.get_file_info)
            .map2(self.__image_file_utility.close_file(image), lambda file_info, _: file_info)
            .abind(lambda file_info: self.__aupload_file(f"{asset.user.id}/converter/converted", file_info))
            .abind(lambda info_url_pair: self.__acreate_asset_file(ConverterConvertedImageAssetFile, *info_url_pair, asset)),
            lambda original, converted: ConversionResponse(
                original_data=ConversionResponse.ImageData.from_asset_file(original),
                converted_data=ConversionResponse.ImageData.from_asset_file(converted),
            ),
        )

    @acontext_result
    async def __aupload_file(self, path_to_upload: str, file_info: ImageFileInfo) -> ContextResult[tuple[ImageFileInfo, str]]:
        public_id = f"{path_to_upload}/{file_info.file_basename}"
        return await self.__cloudinary_service.aupload_file(public_id, file_info.file_content).map(lambda file_url: (file_info, file_url))

    @acontext_result
    async def __acreate_asset_file[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        self,
        asset_file_type: type[T],
        file_info: ImageFileInfo,
        file_url: str,
        asset: ConverterImageAsset,
    ) -> ContextResult[T]:
        return await self.__converter_repository.acreate_asset_file(asset_file_type, file_info, file_url, asset)
