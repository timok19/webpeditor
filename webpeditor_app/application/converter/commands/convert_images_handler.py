import asyncio
from PIL import Image
from PIL.ImageFile import ImageFile
from ninja import UploadedFile
from types_linq import Enumerable
from typing import IO, Final, cast, final, Callable

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

    async def handle_async(
        self,
        request: ConversionRequest,
        session_service: SessionService,
    ) -> EnumerableContextResult[ConversionResponse]:
        return (
            await self.__conversion_request_validator.validate(request)
            .to_context_result()
            .bind_async(lambda _: session_service.get_user_id_async())
            .bind_many_async(lambda user_id: self.__batch_convert_async(user_id, request))
        )

    async def __batch_convert_async(
        self,
        user_id: str,
        request: ConversionRequest,
    ) -> EnumerableContextResult[ConversionResponse]:
        return (
            EnumerableContextResult[ConversionResponse]
            .from_results(
                await asyncio.gather(
                    *Enumerable(request.files)
                    .chunk(4)
                    .select_many(lambda files: [self.__convert_async(user_id, file, request.options) for file in files])
                    .to_list()
                )
            )
            .match(self.__process_values(user_id), self.__process_errors(user_id))
        )

    # TODO: fix problem with empty filename
    async def __convert_async(
        self,
        user_id: str,
        uploaded_file: UploadedFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        with Image.open(cast(IO[bytes], uploaded_file.file)) as image:
            return await (
                self.__cleanup_previous_images(user_id)
                .bind_async(self.__user_repository.get_user_async)
                .bind_async(self.__converter_repository.create_asset_async)
                .bind(
                    lambda asset: self.__image_file_utility.normalize_filename(uploaded_file.name)
                    .bind(lambda cleaned_filename: self.__image_file_utility.update_filename(image, cleaned_filename))
                    .map(lambda updated_image: (updated_image, asset))
                )
                .bind_async(lambda image_asset_pair: self.__convert_and_store(image_asset_pair, options))
                .map(self.__to_response)
            )

    def __cleanup_previous_images(self, user_id: str) -> AwaitableContextResult[str]:
        async def cleanup_async(asset_exists: bool) -> ContextResult[str]:
            return (
                await AwaitableContextResult(self.__converter_repository.delete_asset_async(user_id))
                .map_async(lambda _: self.__cloudinary_service.delete_assets(user_id))
                .map(lambda _: user_id)
                if asset_exists
                else ContextResult[str].success(user_id)
            )

        return AwaitableContextResult(self.__converter_repository.asset_exists_async(user_id)).bind_async(cleanup_async)

    def __convert_and_store(
        self,
        image_asset_pair: tuple[ImageFile, ConverterImageAsset],
        options: ConversionRequest.Options,
    ) -> AwaitableContextResult[tuple[ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile]]:
        image, asset = image_asset_pair
        converted_type = ConverterConvertedImageAssetFile
        original_type = ConverterOriginalImageAssetFile
        return (
            self.__converter_service.get_info(image)
            .bind_async(lambda i: self.__converter_repository.create_asset_file_async(original_type, i, asset))
            .bind_async(
                lambda original: self.__converter_service.convert_image(image, options)
                .bind_async(lambda i: self.__converter_repository.create_asset_file_async(converted_type, i, asset))
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

    def __process_values(
        self,
        user_id: str,
    ) -> Callable[[Enumerable[ConversionResponse]], Enumerable[ConversionResponse]]:
        def process(values: Enumerable[ConversionResponse]) -> Enumerable[ConversionResponse]:
            self.__logger.log_info(f"Successfully converted {values.count()} image(s) for user '{user_id}'")
            return values

        return process

    def __process_errors(
        self,
        user_id: str,
    ) -> Callable[[Enumerable[ErrorContext]], Enumerable[ErrorContext]]:
        def process(errors: Enumerable[ErrorContext]) -> Enumerable[ErrorContext]:
            reasons = "; ".join(errors.select(lambda error: error.to_str()))
            self.__logger.log_error(f"Failed to convert images for user '{user_id}'. [{reasons}]")
            return errors

        return process
