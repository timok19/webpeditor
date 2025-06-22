import asyncio

from PIL import Image
from PIL.ImageFile import ImageFile
from types_linq import Enumerable
from typing import Final, final

from webpeditor_app.application.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.application.converter.services.abc.image_converter_abc import ImageConverterABC
from webpeditor_app.application.converter.schemas import ConversionRequest, ConversionResponse

from webpeditor_app.application.common.abc.validator_abc import ValidatorABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import (
    ContextResult,
    EnumerableContextResult,
    ErrorContext,
    acontext_result,
    aenumerable_context_result,
)
from webpeditor_app.application.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.globals import Unit
from webpeditor_app.infrastructure.abc.converter_repository_abc import ConverterRepositoryABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.models.converter import (
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
    ConverterConvertedImageAssetFile,
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

    async def ahandle(
        self,
        request: ConversionRequest,
        session_service: SessionService,
    ) -> EnumerableContextResult[ConversionResponse]:
        return await (
            self.__conversion_request_validator.validate(request)
            .to_context_result()
            .abind(lambda _: session_service.asynchronize())
            .abind_many2(lambda user_id: self.__aconvert_files(user_id, request))
        )

    @aenumerable_context_result
    async def __aconvert_files(
        self,
        user_id: str,
        request: ConversionRequest,
    ) -> EnumerableContextResult[ConversionResponse]:
        def log_success(values: Enumerable[ConversionResponse]) -> Enumerable[ConversionResponse]:
            self.__logger.log_info(f"Successfully converted {values.count()} image(s) for user '{user_id}'")
            return values

        def log_errors(errors: Enumerable[ErrorContext]) -> Enumerable[ErrorContext]:
            reasons = "; ".join(errors.select(lambda error: error.to_str()))
            self.__logger.log_error(f"Failed to convert images for user '{user_id}'. [{reasons}]")
            return errors

        return await (
            self.__acleanup_previous_images(user_id)
            .abind(lambda _: self.__user_repository.aget(user_id))
            .abind(self.__converter_repository.aget_or_create_asset)
            .map(lambda asset: (Enumerable(request.files), asset))
            .map(
                lambda pair: pair[0].select(
                    lambda file: self.__image_file_utility.normalize_filename(file.name)
                    .bind(lambda normalized: self.__image_file_utility.update_filename(Image.open(file), normalized))
                    .abind(lambda updated_image: self.__aconvert_and_save(updated_image, pair[1], request.options))
                ),
            )
            .amap(lambda results: asyncio.gather(*results))
            .abind_many(EnumerableContextResult[ConversionResponse].from_results)
            .match(log_success, log_errors)
        )

    @acontext_result
    async def __acleanup_previous_images(self, user_id: str) -> ContextResult[Unit]:
        return await self.__converter_repository.aasset_exists(user_id).aif_then_else(
            lambda exists: not exists,
            lambda _: ContextResult[Unit].success(Unit()),
            lambda _: self.__converter_repository.adelete_asset(user_id).abind(
                lambda _: self.__cloudinary_service.adelete_resource_recursively(user_id, "converter")
            ),
        )

    @acontext_result
    async def __aconvert_and_save(
        self,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        return await self.__acreate_original_asset_file(asset.user.id, image, asset).amap3(
            self.__aconvert_and_save_asset_file(asset.user.id, image, asset, options),
            lambda original, converted: ConversionResponse(
                original_data=ConversionResponse.ImageData.from_asset_file(original),
                converted_data=ConversionResponse.ImageData.from_asset_file(converted),
            ),
        )

    @acontext_result
    async def __acreate_original_asset_file(
        self,
        user_id: str,
        image: ImageFile,
        asset: ConverterImageAsset,
    ) -> ContextResult[ConverterOriginalImageAssetFile]:
        return await self.__image_file_utility.get_file_info(image).abind(
            lambda file_info: self.__cloudinary_service.aupload_file(
                f"{user_id}/converter/original/{file_info.file_basename}",
                file_info.file_content,
            ).abind(
                lambda file_url: self.__converter_repository.acreate_asset_file(
                    ConverterOriginalImageAssetFile,
                    file_info,
                    file_url,
                    asset,
                )
            )
        )

    @acontext_result
    async def __aconvert_and_save_asset_file(
        self,
        user_id: str,
        image: ImageFile,
        asset: ConverterImageAsset,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConverterConvertedImageAssetFile]:
        return await (
            self.__converter_service.convert_image(image, options)
            .bind(self.__image_file_utility.get_file_info)
            .map2(self.__image_file_utility.close_file(image), lambda file_info, _: file_info)
            .abind(
                lambda file_info: self.__cloudinary_service.aupload_file(
                    f"{user_id}/converter/converted/{file_info.file_basename}",
                    file_info.file_content,
                ).abind(
                    lambda file_url: self.__converter_repository.acreate_asset_file(
                        ConverterConvertedImageAssetFile,
                        file_info,
                        file_url,
                        asset,
                    )
                )
            )
        )
