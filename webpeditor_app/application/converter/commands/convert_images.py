import asyncio
import os.path
from decimal import Decimal
from io import BytesIO
from typing import Final, Union, final, cast

from PIL.Image import Image, alpha_composite, new, open as open_image
from PIL.ImageFile import ImageFile
from expression import Option
from ninja import UploadedFile
from types_linq import Enumerable

from webpeditor_app.application.auth.session_service import SessionService
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest, ConversionResponse
from webpeditor_app.application.converter.schemas.settings import (
    ImageConverterAllOutputFormats,
    ImageConverterOutputFormats,
    ImageConverterOutputFormatsWithAlphaChannel,
)
from webpeditor_app.common.abc.image_file_utility_abc import ImageFileUtilityABC
from webpeditor_app.common.abc.validator_abc import ValidatorABC
from webpeditor_app.common.image_file.schemas.image_file import ImageFileInfo
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import ContextResult, ErrorContext, MultipleContextResults
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
    ) -> MultipleContextResults[ConversionResponse]:
        # Synchronize session
        await session_service.synchronize_async()

        # Request validation
        validation_result = self.__conversion_request_validator.validate(request).to_context_result()
        if validation_result.is_error():
            return MultipleContextResults[ConversionResponse].from_results(
                ContextResult[ConversionResponse].Error(validation_result.error)
            )

        # Get User ID
        user_id_result = await session_service.get_user_id_async()
        if user_id_result.is_error():
            return MultipleContextResults[ConversionResponse].from_results(
                ContextResult[ConversionResponse].Error(user_id_result.error)
            )

        # Delete previous content if exist
        converter_asset = ConverterImageAsset.objects.filter(user_id=user_id_result.ok)
        if await converter_asset.aexists():
            self.__cloudinary_service.delete_converted_images(user_id_result.ok)
            await converter_asset.adelete()

        # Process images
        return (await self.__batch_convert_async(user_id_result.ok, request)).match(
            lambda values: self.__process_values(values, user_id_result.ok),
            lambda errors: self.__process_errors(errors, user_id_result.ok),
        )

    async def __batch_convert_async(
        self,
        user_id: str,
        request: ConversionRequest,
    ) -> MultipleContextResults[ConversionResponse]:
        return MultipleContextResults[ConversionResponse].from_results(
            *await asyncio.gather(
                *Enumerable(request.files)
                .chunk(4)
                .select_many(lambda files: [self.__convert_async(user_id, file, request.options) for file in files])
                .to_list()
            )
        )

    def __process_values(
        self,
        values: Enumerable[ConversionResponse],
        user_id: str,
    ) -> Enumerable[ConversionResponse]:
        self.__logger.log_info(f"Successfully converted {values.count()} image(s) for user '{user_id}'")
        return values

    def __process_errors(
        self,
        errors: Enumerable[ErrorContext],
        user_id: str,
    ) -> Enumerable[ErrorContext]:
        # Aggregate reasons of errors into a single string for each user
        reasons = errors.select(lambda error: error.to_str()).aggregate(lambda m1, m2: f"{m1}, {m2}")
        self.__logger.log_error(f"Failed to convert images for user '{user_id}'. {reasons}")
        return errors

    async def __convert_async(
        self,
        user_id: str,
        uploaded_file: UploadedFile,
        options: ConversionRequest.Options,
    ) -> ContextResult[ConversionResponse]:
        # Get filenames
        original_filename = self.__image_file_utility.sanitize_filename(uploaded_file.name)
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
        with open_image(uploaded_file.file) as original_image:
            original_file_info_result = self.__get_file_info(original_image, original_filename)
            converted_file_info_result = (
                self.__convert_color_mode(original_image, options.output_format)
                .map(lambda image: self.__convert_format(image, options))
                .bind(lambda image: self.__get_file_info(image, new_filename))
            )

        if original_file_info_result.is_error():
            return ContextResult[ConversionResponse].Error(original_file_info_result.error)

        if converted_file_info_result.is_error():
            return ContextResult[ConversionResponse].Error(converted_file_info_result.error)

        # Get or create converter image asset
        converter_image_asset_result = await self.__get_or_create_image_asset_async(user_id)
        if converter_image_asset_result.is_error():
            return ContextResult[ConversionResponse].Error(converter_image_asset_result.error)

        # Create original image asset file
        original_image_data_result = (
            await converter_image_asset_result.map_async(
                lambda asset: self.__create_asset_file_async(
                    original_file_info_result.ok,
                    original_filename,
                    original_trimmed_filename,
                    asset,
                    ConverterOriginalImageAssetFile,
                )
            )
        ).map(self.__to_image_data)

        if original_image_data_result.is_error():
            return ContextResult[ConversionResponse].Error(original_image_data_result.error)

        # Create converted image asset file
        converted_image_data_result = (
            await converter_image_asset_result.map_async(
                lambda asset: self.__create_asset_file_async(
                    converted_file_info_result.ok,
                    f"converted_{new_filename}",
                    new_trimmed_filename,
                    asset,
                    ConverterConvertedImageAssetFile,
                )
            )
        ).map(self.__to_image_data)

        if converted_image_data_result.is_error():
            return ContextResult[ConversionResponse].Error(converted_image_data_result.error)

        return ContextResult[ConversionResponse].Ok(
            ConversionResponse(
                original_image_data=original_image_data_result.ok,
                converted_image_data=converted_image_data_result.ok,
            )
        )

    @staticmethod
    def __create_new_filename(filename: str, *, options: ConversionRequest.Options) -> str:
        basename, _ = os.path.splitext(filename)
        return f"webpeditor_{basename}.{options.output_format.lower()}"

    def __trim_filename_or_default(self, filename: str, *, max_length: int, output_format: str) -> str:
        default = f"webpeditor.{output_format.lower()}"
        return self.__image_file_utility.trim_filename(filename, max_length=max_length).default_value(default)

    def __get_file_info(self, image: ImageFile, filename: str) -> ContextResult[ImageFileInfo]:
        return self.__image_file_utility.update_filename(image, filename).bind(self.__image_file_utility.get_file_info)

    @staticmethod
    async def __get_or_create_image_asset_async(user_id: str) -> ContextResult[ConverterImageAsset]:
        optional_user = await AppUser.objects.filter(id=user_id).afirst()
        user_result = Option.of_optional(optional_user).to_result(
            ErrorContext.not_found(f"Unable to find current user '{user_id}'")
        )
        converter_image_asset_result = (
            await ContextResult[AppUser]
            .from_result(user_result)
            .map_async(lambda user: ConverterImageAsset.objects.aget_or_create(user=user))
        )
        return converter_image_asset_result.map(lambda image_asset: image_asset[0])

    @staticmethod
    async def __create_asset_file_async(
        file_info: ImageFileInfo,
        new_filename: str,
        trimmed_filename: str,
        converter_image_asset: ConverterImageAsset,
        asset_file_model: type[Union[ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile]],
    ) -> Union[ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile]:
        # TODO: Make sure that the file size of the converted image is not greater than 10485760
        return await asset_file_model.objects.acreate(
            file=file_info.content_file,
            filename=new_filename,
            filename_shorter=trimmed_filename,
            content_type=f"image/{file_info.file_format.lower()}",
            format=file_info.file_format,
            format_description=file_info.file_format_description or "",
            size=file_info.size,
            width=file_info.width,
            height=file_info.height,
            aspect_ratio=file_info.aspect_ratio,
            color_mode=file_info.color_mode,
            exif_data=file_info.exif_data,
            image_asset=converter_image_asset,
        )

    @staticmethod
    def __to_image_data(
        asset_file: Union[ConverterOriginalImageAssetFile, ConverterConvertedImageAssetFile],
    ) -> ConversionResponse.ImageData:
        return ConversionResponse.ImageData(
            url=asset_file.file.url,
            filename=str(asset_file.filename),
            filename_shorter=str(asset_file.filename_shorter),
            content_type=str(asset_file.content_type),
            format=str(asset_file.format),
            format_description=str(asset_file.format_description),
            size=asset_file.size or 0,
            width=asset_file.width or 0,
            height=asset_file.height or 0,
            aspect_ratio=asset_file.aspect_ratio or Decimal(),
            color_mode=str(asset_file.color_mode),
            exif_data=asset_file.exif_data,
        )

    def __convert_color_mode(
        self,
        original_image: Image,
        output_format: ImageConverterAllOutputFormats,
    ) -> ContextResult[Image]:
        if original_image.format is None:
            return ContextResult[Image].Error(
                ErrorContext.server_error("Unable to convert image color. Invalid image format")
            )

        if original_image.format.upper() not in ImageConverterOutputFormatsWithAlphaChannel:
            return ContextResult[Image].Ok(original_image.convert("RGB"))

        rgba_image = original_image.convert("RGBA")

        if output_format in ImageConverterOutputFormatsWithAlphaChannel:
            return ContextResult[Image].Ok(rgba_image)

        return ContextResult[Image].Ok(self.__to_rgb(rgba_image))

    @staticmethod
    def __to_rgb(rgba_image: Image) -> Image:
        white_color = (255, 255, 255, 255)
        white_background: Image = new(mode="RGBA", size=rgba_image.size, color=white_color)
        # Merge RGBA into RGB with a white background
        return alpha_composite(white_background, rgba_image).convert("RGB")

    @staticmethod
    def __convert_format(image: Image, options: ConversionRequest.Options) -> ImageFile:
        buffer = BytesIO()

        match options.output_format:
            case ImageConverterAllOutputFormats.JPEG:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.JPEG,
                    quality=options.quality,
                    subsampling=0 if options.quality == 100 else 2,
                    exif=image.getexif(),
                    optimize=True,
                )
            case ImageConverterAllOutputFormats.TIFF:
                image.save(
                    buffer,
                    format=ImageConverterOutputFormats.TIFF,
                    quality=options.quality,
                    exif=image.getexif(),
                    optimize=True,
                    compression="jpeg" if image.format == ImageConverterAllOutputFormats.JPEG else None,
                )
            case ImageConverterAllOutputFormats.BMP:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.BMP,
                    bitmap_format="bmp",
                    optimize=True,
                )
            case ImageConverterAllOutputFormats.PNG:
                image.save(
                    buffer,
                    format=ImageConverterAllOutputFormats.PNG,
                    bitmap_format="png",
                    exif=image.getexif(),
                    optimize=True,
                )
            case _:
                image.save(
                    buffer,
                    format=options.output_format,
                    quality=options.quality,
                    exif=image.getexif(),
                    optimize=True,
                )

        # Set pointer to start
        buffer.seek(0)
        return open_image(buffer)
