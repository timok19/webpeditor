import os.path
from decimal import Decimal
from io import BytesIO
from typing import IO, Collection, Final, Type, cast, final

from PIL.Image import Image, alpha_composite, new, open
from PIL.ImageFile import ImageFile
from ninja import UploadedFile
from returns.pipeline import is_successful
from returns.result import Result
from types_linq import Enumerable

from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.extensions.result_extensions import ResultExtensions, FailureContext, ResultOfType
from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.application.converter.schemas.conversion import (
    ConversionRequest,
    ConversionResponse,
    OriginalAndConvertedImageFileInfo,
)
from webpeditor_app.application.converter.schemas.settings import (
    ImageConverterAllOutputFormats,
    ImageConverterOutputFormats,
    ImageConverterOutputFormatsWithAlphaChannel,
)
from webpeditor_app.infrastructure.abc.cloudinary_service_abc import CloudinaryServiceABC
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ConvertImages:
    def __init__(self) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)
        self.__cloudinary_service: Final[CloudinaryServiceABC] = DiContainer.get_dependency(CloudinaryServiceABC)
        self.__image_file_utility: Final[ImageFileUtilityABC] = DiContainer.get_dependency(ImageFileUtilityABC)
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = DiContainer.get_dependency(
            ValidatorABC[ConversionRequest]
        )

    async def handle_async(
        self,
        request: ConversionRequest,
        session_service: SessionService,
    ) -> Collection[ResultOfType[ConversionResponse]]:
        # Synchronize session
        await session_service.synchronize_async()

        # Request validation
        validation_result = self.__conversion_request_validator.validate(request).as_based_result()
        if not is_successful(validation_result):
            return [ResultExtensions.from_failure(validation_result.failure())]

        # Get User ID
        user_id_result = await session_service.get_user_id_async()
        if not is_successful(user_id_result):
            return [ResultExtensions.from_failure(user_id_result.failure())]

        user_id = user_id_result.unwrap()

        # Delete previous content if exist
        converted_image_asset = ConverterImageAsset.objects.filter(user_id=user_id)
        if await converted_image_asset.aexists():
            await converted_image_asset.adelete()
            self.__cloudinary_service.delete_converted_images(user_id)

        # Process images
        return ResultExtensions.match(
            await self.__batch_convert_async(request, user_id),
            lambda responses: self.__process_successes(responses, user_id),
            lambda failures: self.__process_failures(failures, user_id),
        )

    async def __batch_convert_async(
        self,
        request: ConversionRequest,
        user_id: str,
    ) -> Enumerable[ResultOfType[ConversionResponse]]:
        return Enumerable(
            [
                await result
                for result in Enumerable(request.files)
                .chunk(4)
                .select_many(
                    lambda files: Enumerable(files).select(
                        lambda file: self.__convert_async(user_id, file, request.options)
                    )
                )
            ]
        )

    def __process_successes(
        self,
        responses: Enumerable[ConversionResponse],
        user_id: str,
    ) -> Collection[ResultOfType[ConversionResponse]]:
        self.__logger.log_info(f"Successfully converted {responses.count()} image(s) for user '{user_id}'")
        return responses.select(ResultExtensions.success)

    def __process_failures(
        self,
        failures: Enumerable[FailureContext],
        user_id: str,
    ) -> Enumerable[ResultOfType[ConversionResponse]]:
        failures_messages = failures.select(
            lambda failure: f"Error code: {failure.error_code}, Message: {failure.message or ''}"
        )

        error_code = failures.select(lambda failure: failure.error_code).first()

        self.__logger.log_error(
            f"Failed to convert images for user '{user_id}'. Reasons: [{', '.join(failures_messages)}] "
        )

        return failures.select(
            lambda failure: ResultExtensions.failure(
                error_code,
                f"Failed to convert images. Reasons: [{', '.join(failures_messages)}]",
            )
        )

    async def __convert_async(
        self,
        user_id: str,
        file: UploadedFile,
        options: ConversionRequest.Options,
    ) -> ResultOfType[ConversionResponse]:
        # Get sanitized filenames
        original_filename = self.__image_file_utility.sanitize_filename(cast(str, file.name))
        new_filename = self.__create_new_filename(original_filename, options=options)

        # Trim original and new filenames
        max_length: Final[int] = 25
        original_trimmed_filename = self.__trim_filename_or_default(
            original_filename,
            max_length=max_length,
            output_format=options.output_format,
        )
        new_trimmed_filename = self.__trim_filename_or_default(
            f"converted_{new_filename}",
            max_length=max_length,
            output_format=options.output_format,
        )

        # Get original and converted image data
        with open(cast(IO, file.file)) as original_image:
            image_files_info_results = Result.do(
                OriginalAndConvertedImageFileInfo(original=original_file_info, converted=converted_file_info)
                for original_file_info in (
                    self.__image_file_utility.update_filename(original_image, new_filename).bind(
                        self.__image_file_utility.get_file_info
                    )
                )
                for converted_file_info in (
                    self.__convert_color_mode(original_file_info.image_file, output_format=options.output_format)
                    .map(lambda image: self.__convert_format(image, options))
                    .bind(lambda image: self.__image_file_utility.update_filename(image, new_filename))
                    .bind(self.__image_file_utility.get_file_info)
                )
            )

        if not is_successful(image_files_info_results):
            return ResultExtensions.from_failure(image_files_info_results.failure())

        # Get or create converter image asset
        converter_image_asset_result = await self.__get_or_create_image_asset_async(user_id)
        if not is_successful(converter_image_asset_result):
            return ResultExtensions.from_failure(converter_image_asset_result.failure())

        # Create original image asset file
        original_image_data = await self.__create_asset_file_data_async(
            image_files_info_results.unwrap().original,
            original_filename,
            original_trimmed_filename,
            converter_image_asset_result.unwrap(),
            ConverterOriginalImageAssetFile,
        )

        # Create converted image asset file
        converted_image_data = await self.__create_asset_file_data_async(
            image_files_info_results.unwrap().converted,
            f"converted_{new_filename}",
            new_trimmed_filename,
            converter_image_asset_result.unwrap(),
            ConverterConvertedImageAssetFile,
        )

        return ResultExtensions.success(
            ConversionResponse(
                original_image_data=original_image_data,
                converted_image_data=converted_image_data,
            )
        )

    @staticmethod
    def __create_new_filename(filename: str, *, options: ConversionRequest.Options) -> str:
        basename, _ = os.path.splitext(filename)
        return f"webpeditor_{basename}.{options.output_format.lower()}"

    def __trim_filename_or_default(self, filename: str, *, max_length: int, output_format: str) -> str:
        return self.__image_file_utility.trim_filename(filename, max_length=max_length).value_or(
            f"webpeditor.{output_format.lower()}"
        )

    @staticmethod
    async def __get_or_create_image_asset_async(user_id: str) -> ResultOfType[ConverterImageAsset]:
        user = await AppUser.objects.filter(id=user_id).afirst()
        if user is None:
            return ResultExtensions.failure(
                FailureContext.ErrorCode.NOT_FOUND,
                f"Unable to find current user '{user_id}'",
            )

        converter_image_asset, _ = await ConverterImageAsset.objects.aget_or_create(user=user)
        return ResultExtensions.success(converter_image_asset)

    @staticmethod
    async def __create_asset_file_data_async[T: (ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile)](
        file_info: ImageFileInfo,
        new_filename: str,
        trimmed_filename: str,
        converter_image_asset: ConverterImageAsset,
        asset_file_model: Type[T],
    ) -> ConversionResponse.ImageData:
        created_asset_file = await asset_file_model.objects.acreate(
            file=file_info.content_file,
            filename=new_filename,
            filename_shorter=trimmed_filename,
            content_type=f"image/{file_info.file_format.lower()}",
            format=file_info.file_format,
            format_description=file_info.file_format_description or "",
            size=file_info.size,
            width=file_info.resolution[0],
            height=file_info.resolution[1],
            aspect_ratio=file_info.aspect_ratio,
            color_mode=file_info.color_mode,
            exif_data=file_info.exif_data,
            image_asset=converter_image_asset,
        )

        return ConversionResponse.ImageData(
            url=created_asset_file.file.url,
            filename=created_asset_file.filename,
            filename_shorter=created_asset_file.filename_shorter,
            content_type=created_asset_file.content_type,
            format=created_asset_file.format,
            format_description=created_asset_file.format_description,
            size=created_asset_file.size or 0,
            resolution=(created_asset_file.width or 0, created_asset_file.height or 0),
            aspect_ratio=created_asset_file.aspect_ratio or Decimal.from_float(0),
            color_mode=created_asset_file.color_mode,
            exif_data=created_asset_file.exif_data,
        )

    def __convert_color_mode(
        self,
        original_image: Image,
        output_format: ImageConverterAllOutputFormats,
    ) -> ResultOfType[Image]:
        if original_image.format is None:
            return ResultExtensions.failure(
                FailureContext.ErrorCode.INTERNAL_SERVER_ERROR,
                "Unable to convert image color. Invalid image format",
            )

        if original_image.format.upper() not in ImageConverterOutputFormatsWithAlphaChannel:
            return ResultExtensions.success(original_image.convert("RGB"))

        rgba_image = original_image.convert("RGBA")

        if output_format in ImageConverterOutputFormatsWithAlphaChannel:
            return ResultExtensions.success(rgba_image)

        return ResultExtensions.success(self.__to_rgb(rgba_image))

    @staticmethod
    def __to_rgb(rgba_image: Image) -> Image:
        white_color = (255, 255, 255, 255)
        white_background: Image = new(mode="RGBA", size=rgba_image.size, color=white_color)
        # Merge RGBA into RGB with a white background
        return alpha_composite(white_background, rgba_image).convert("RGB")

    @staticmethod
    def __convert_format(image: Image, options: ConversionRequest.Options) -> ImageFile:
        with BytesIO() as buffer:
            match options.output_format:
                case ImageConverterAllOutputFormats.JPEG:
                    image.save(
                        buffer,
                        format=ImageConverterAllOutputFormats.JPEG,
                        quality=options.quality,
                        subsampling=0 if options.quality == 100 else 2,
                        exif=image.getexif(),
                    )
                case ImageConverterAllOutputFormats.TIFF:
                    image.save(
                        buffer,
                        format=ImageConverterOutputFormats.TIFF,
                        quality=options.quality,
                        exif=image.getexif(),
                        compression="jpeg",
                    )
                case ImageConverterAllOutputFormats.BMP:
                    image.save(
                        buffer,
                        format=ImageConverterAllOutputFormats.BMP,
                        bitmap_format="bmp",
                    )
                case ImageConverterAllOutputFormats.PNG:
                    image.save(
                        buffer,
                        format=ImageConverterAllOutputFormats.PNG,
                        bitmap_format="png",
                        exif=image.getexif(),
                    )
                case _:
                    image.save(
                        buffer,
                        format=options.output_format,
                        quality=options.quality,
                        exif=image.getexif(),
                        optimize=True,
                    )

            return open(buffer)
