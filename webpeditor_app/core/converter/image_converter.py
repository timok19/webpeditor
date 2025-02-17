import os.path
from decimal import Decimal
from io import BytesIO
from typing import Collection, Final, Type, final

from PIL.ImageFile import ImageFile
from ninja import UploadedFile
from PIL.Image import Exif, Image, alpha_composite, new, open
from returns.pipeline import is_successful
from returns.result import Failure, Success, Result
from types_linq import Enumerable

from webpeditor_app.common.abc.image_file_utility_service import ImageFileUtilityServiceABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.common.result_extensions import FailureContext, ValueResult
from webpeditor_app.common.validator_abc import ValidatorABC
from webpeditor_app.core.abc.image_converter import ImageConverterABC
from webpeditor_app.core.abc.webpeditorlogger import WebPEditorLoggerABC
from webpeditor_app.core.auth.session_service import SessionService
from webpeditor_app.core.converter.schemas.conversion import ConversionRequest, ConversionResponse
from webpeditor_app.core.converter.schemas.download import DownloadAllZipResponse
from webpeditor_app.core.converter.settings import (
    ImageConverterAllOutputFormats,
    ImageConverterOutputFormats,
    ImageConverterOutputFormatsWithAlphaChannel,
)
from webpeditor_app.infrastructure.abc.cloudinary_service import CloudinaryServiceABC
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@final
class ImageConverter(ImageConverterABC):
    def __init__(self) -> None:
        from webpeditor_app.common.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)
        self.__cloudinary_service: Final[CloudinaryServiceABC] = DiContainer.get_dependency(CloudinaryServiceABC)
        self.__image_file_utility_service: Final[ImageFileUtilityServiceABC] = DiContainer.get_dependency(
            ImageFileUtilityServiceABC
        )
        self.__conversion_request_validator: Final[ValidatorABC[ConversionRequest]] = DiContainer.get_dependency(
            ValidatorABC[ConversionRequest]
        )
        self.__number_of_threads_for_batch_processing: Final[int] = 2

    async def convert_async(
        self,
        request: ConversionRequest,
        session_service: SessionService,
    ) -> Collection[ValueResult[ConversionResponse]]:
        # Synchronize session
        await session_service.synchronize_async()

        # Validation
        validation_result = self.__conversion_request_validator.validate(request)
        if not validation_result.is_successful():
            return [
                Failure(
                    FailureContext(
                        error_code=FailureContext.ErrorCode.BAD_REQUEST,
                        message=validation_result.message,
                    )
                )
            ]

        # Get User ID
        user_id_result = await session_service.get_user_id_async()
        if not is_successful(user_id_result):
            return [Failure(user_id_result.failure())]

        converted_image_asset_query_set = ConverterImageAsset.objects.filter(user_id=user_id_result.unwrap())

        # Delete previous content if exist
        if await converted_image_asset_query_set.aexists():
            await converted_image_asset_query_set.adelete()
            self.__cloudinary_service.delete_converted_images(user_id_result.unwrap())

        # Process images
        future_results = (
            Enumerable(request.files)
            .chunk(min(len(request.files), self.__number_of_threads_for_batch_processing))
            .select_many(
                lambda image_files_batch: [
                    self.__convert_async(
                        user_id_result.unwrap(),
                        image_file,
                        options=request.options,
                    )
                    for image_file in image_files_batch
                ]
            )
        )

        # Get results
        results = Enumerable([await future_result for future_result in future_results])

        # Get failed results
        if results.any(lambda result: not is_successful(result)):
            errors = results.where(lambda result: not is_successful(result))
            error_messages = errors.select(
                lambda error: f"Error code: {error.failure().error_code}, Message: {error.failure().message or ''}"
            )

            self.__logger.log_error(
                f"Failed to convert images for user '{user_id_result.unwrap()}'. Reasons: [{', '.join(*error_messages)}] "
            )

            return [
                Failure(
                    FailureContext(
                        message=f"Failed to convert images. Reasons: [{', '.join(*error_messages)}]",
                        error_code=errors.select(lambda error: error.failure().error_code).first(),
                    )
                )
            ]

        self.__logger.log_info(
            f"Successfully converted {results.count()} image(s) for user '{user_id_result.unwrap()}'"
        )

        return results.to_list()

    # TODO Finish the implementation
    async def download_all_as_zip_async(self, session_service: SessionService) -> ValueResult[DownloadAllZipResponse]:
        # Synchronize session
        await session_service.synchronize_async()

        (await session_service.get_user_id_async()).map(
            lambda user_id: ConverterConvertedImageAssetFile.objects.filter(image_asset__user__id=user_id).all().aget()
        )

        return Success(DownloadAllZipResponse(zip_file_url=""))

    async def __convert_async(
        self,
        user_id: str,
        uploaded_image_file: UploadedFile,
        *,
        options: ConversionRequest.Options,
    ) -> ValueResult[ConversionResponse]:
        if uploaded_image_file.name is None:
            return Failure(
                FailureContext(
                    error_code=FailureContext.ErrorCode.BAD_REQUEST,
                    message="Invalid image file",
                )
            )

        # Get sanitized filenames
        original_filename = self.__image_file_utility_service.sanitize_filename(uploaded_image_file.name)
        new_filename = self.__create_new_filename(original_filename, options=options)

        # Trim original and new filenames
        max_length: Final[int] = 25
        original_trimmed_filename = self.__trim_filename_or_default(
            original_filename,
            max_length=max_length,
            output_format=options.output_format,
        )
        new_trimmed_filename = f"converted_{self.__trim_filename_or_default(new_filename, max_length=max_length, output_format=options.output_format)}"

        # Get original and converted images
        if not is_successful(
            original_and_converted_image_data_result := Result.do(
                (original_image_data, converted_image_data)
                for original_image_data in self.__get_original_image_data(uploaded_image_file, new_filename)
                for converted_image_data in self.__convert_image(
                    original_image_data.image_file, new_filename, options=options
                )
            )
        ):
            return Failure(original_and_converted_image_data_result.failure())

        original_image_data, converted_image_data = original_and_converted_image_data_result.unwrap()

        # Fetch the user instance using the provided user_id
        user = await AppUser.objects.filter(id=user_id).afirst()
        if user is None:
            return Failure(
                FailureContext(
                    message="Unable to find current user",
                    error_code=FailureContext.ErrorCode.INTERNAL_SERVER_ERROR,
                )
            )

        converter_image_asset, _ = await ConverterImageAsset.objects.aget_or_create(user=user)

        original_image_data = await self.__create_asset_file_data_async(
            original_image_data,
            original_filename,
            original_trimmed_filename,
            converter_image_asset,
            ConverterOriginalImageAssetFile,
        )

        converted_image_data = await self.__create_asset_file_data_async(
            converted_image_data,
            f"converted_{new_filename}",
            new_trimmed_filename,
            converter_image_asset,
            ConverterConvertedImageAssetFile,
        )

        return Success(
            ConversionResponse(
                original_image_data=original_image_data,
                converted_image_data=converted_image_data,
            )
        )

    @staticmethod
    def __create_new_filename(filename: str, *, options: ConversionRequest.Options) -> str:
        basename, _ = os.path.splitext(filename)
        return f"webpeditor_{basename}.{options.output_format.lower()}"

    def __trim_filename_or_default(
        self,
        filename: str,
        *,
        max_length: int,
        output_format: str,
    ) -> str:
        return self.__image_file_utility_service.trim_filename(filename, max_length=max_length).value_or(
            f"webpeditor.{output_format.lower()}"
        )

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

    def __convert_image(
        self,
        original_image: ImageFile,
        new_filename: str,
        *,
        options: ConversionRequest.Options,
    ) -> ValueResult[ImageFileInfo]:
        return (
            self.__convert_color_mode(original_image, output_format=options.output_format)
            .map(lambda image: self.__convert_format(image, original_image.getexif(), options=options))
            .bind(lambda image: self.__image_file_utility_service.update_filename(image, new_filename))
            .bind(self.__image_file_utility_service.get_file_info)
        )

    @staticmethod
    def __convert_format(image: Image, exif_data: Exif, options: ConversionRequest.Options) -> ImageFile:
        with BytesIO() as buffer:
            match options.output_format:
                case ImageConverterAllOutputFormats.JPEG:
                    image.save(
                        buffer,
                        format=ImageConverterAllOutputFormats.JPEG,
                        quality=options.quality,
                        subsampling=0 if options.quality == 100 else 2,
                        exif=exif_data,
                    )
                case ImageConverterAllOutputFormats.TIFF:
                    image.save(
                        buffer,
                        format=ImageConverterOutputFormats.TIFF,
                        quality=options.quality,
                        exif=exif_data,
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
                        exif=exif_data,
                    )
                case _:
                    image.save(
                        buffer,
                        format=options.output_format,
                        quality=options.quality,
                        exif=exif_data,
                        optimize=True,
                    )

            return open(buffer)

    def __get_original_image_data(self, image_file: UploadedFile, new_filename: str) -> ValueResult[ImageFileInfo]:
        if image_file.file is None:
            return Failure(
                FailureContext(
                    message="Invalid image file",
                    error_code=FailureContext.ErrorCode.BAD_REQUEST,
                )
            )

        with open(image_file.file) as original_image:
            return self.__image_file_utility_service.update_filename(original_image, new_filename).bind(
                self.__image_file_utility_service.get_file_info
            )

    def __convert_color_mode(
        self,
        original_image: Image,
        *,
        output_format: ImageConverterAllOutputFormats,
    ) -> ValueResult[Image]:
        if original_image.format is None:
            return Failure(
                FailureContext(
                    message="Unable to convert image color. Invalid image format",
                    error_code=FailureContext.ErrorCode.INTERNAL_SERVER_ERROR,
                )
            )

        if original_image.format.upper() not in ImageConverterOutputFormatsWithAlphaChannel:
            return Success(original_image.convert("RGB"))

        rgba_image = original_image.convert("RGBA")

        if output_format in ImageConverterOutputFormatsWithAlphaChannel:
            return Success(rgba_image)

        return Success(self.__to_rgb(rgba_image))

    @staticmethod
    def __to_rgb(rgba_image: Image) -> Image:
        white_color = (255, 255, 255, 255)
        white_background: Image = new(mode="RGBA", size=rgba_image.size, color=white_color)
        # Merge RGBA into RGB with a white background
        return alpha_composite(white_background, rgba_image).convert("RGB")
