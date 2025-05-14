import asyncio
from PIL import Image
from PIL.ImageFile import ImageFile
from ninja import UploadedFile
from types_linq import Enumerable
from typing import Collection, Final, final

from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.application.converter.abc.converter_service_abc import ConverterServiceABC
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest, ConversionResponse

from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import (
    AwaitableContextResult,
    ContextResult,
    ErrorContext,
    EnumerableContextResult,
    AwaitableEnumerableContextResult,
)
from webpeditor_app.common.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
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
        converter_service: ConverterServiceABC,
        image_file_utility: ImageFileUtilityABC,
        converter_repository: ConverterRepositoryABC,
        user_repository: UserRepositoryABC,
        logger: WebPEditorLoggerABC,
    ) -> None:
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = conversion_request_validator
        self.__cloudinary_service: Final[CloudinaryServiceABC] = cloudinary_service
        self.__converter_service: Final[ConverterServiceABC] = converter_service
        self.__image_file_utility: Final[ImageFileUtilityABC] = image_file_utility
        self.__converter_repository: Final[ConverterRepositoryABC] = converter_repository
        self.__user_repository: Final[UserRepositoryABC] = user_repository
        self.__logger: Final[WebPEditorLoggerABC] = logger

    async def ahandle(
        self,
        request: ConversionRequest,
        session_service: SessionService,
    ) -> EnumerableContextResult[ConversionResponse]:
        return (
            await self.__conversion_request_validator.validate(request)
            .to_context_result()
            .abind(lambda _: session_service.aget_unsigned_user_id())
            .abind_many(lambda user_id: self.__abatch_convert(user_id, request))
        )

    async def __abatch_convert(
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

        return (
            await AwaitableEnumerableContextResult[ConversionResponse]
            .afrom_results(
                asyncio.gather(
                    *Enumerable(request.files)
                    .chunk(4)
                    .select_many(lambda files: self.__aconvert(user_id, files, request.options))
                    .to_list()
                )
            )
            .match(log_success, log_errors)
        )

    def __aconvert(
        self,
        user_id: str,
        files: Collection[UploadedFile],
        options: ConversionRequest.Options,
    ) -> Enumerable[AwaitableContextResult[ConversionResponse]]:
        return (
            Enumerable(files)
            .select(lambda file: (Image.open(file), file.name))
            .select(
                lambda image_name_pair: self.__acleanup_previous_images(user_id)
                .abind(self.__user_repository.aget_user)
                .abind(self.__converter_repository.aget_or_create_asset)
                .bind(
                    lambda asset: self.__image_file_utility.normalize_filename(image_name_pair[1])
                    .bind(lambda normalized: self.__image_file_utility.update_filename(image_name_pair[0], normalized))
                    .map(lambda updated_image: (updated_image, asset))
                )
                .abind(lambda image_asset_pair: self.__aconvert_and_store(image_asset_pair, options))
                .map(self.__to_response)
            )
        )

    def __acleanup_previous_images(self, user_id: str) -> AwaitableContextResult[str]:
        async def acleanup_previous_images(asset_exists: bool) -> ContextResult[str]:
            return (
                await self.__converter_repository.adelete_asset(user_id)
                .amap(lambda _: self.__cloudinary_service.adelete_assets(user_id))
                .map(lambda _: user_id)
                if asset_exists
                else ContextResult[str].success(user_id)
            )

        return self.__converter_repository.aasset_exists(user_id).abind(acleanup_previous_images)

    def __aconvert_and_store(
        self,
        image_asset_pair: tuple[ImageFile, ConverterImageAsset],
        options: ConversionRequest.Options,
    ) -> AwaitableContextResult[tuple[ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile]]:
        image, asset = image_asset_pair
        converted_type = ConverterConvertedImageAssetFile
        original_type = ConverterOriginalImageAssetFile
        return (
            self.__converter_service.get_info(image)
            .abind(lambda info: self.__converter_repository.acreate_asset_file(original_type, info, asset))
            .abind(
                lambda original: self.__converter_service.convert_image(image, options)
                .abind(lambda info: self.__converter_repository.acreate_asset_file(converted_type, info, asset))
                .map(lambda converted: (original, converted))
            )
        )

    @staticmethod
    def __to_response(
        original_converted_pair: tuple[ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile],
    ) -> ConversionResponse:
        original_asset_file, converted_asset_file = original_converted_pair
        return ConversionResponse(
            original_data=ConversionResponse.ImageData.from_asset_file(original_asset_file),
            converted_data=ConversionResponse.ImageData.from_asset_file(converted_asset_file),
        )
