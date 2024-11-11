from concurrent.futures import ThreadPoolExecutor, Future, as_completed

from PIL import Image
from PIL.Image import Exif
from PIL.ImageFile import ImageFile
from cloudinary import CloudinaryImage
from injector import inject

from io import BytesIO
from typing import Optional

from django.core.files.uploadedfile import UploadedFile

from webpeditor.settings import ImageConverterSettings
from webpeditor_app.common.image_file.image_file_utility_service_abc import ImageFileUtilityServiceABC
from webpeditor_app.common.resultant import ResultantValue, Resultant, ErrorCode
from webpeditor_app.core.converter.models import ConversionRequest, ConversionResponse, ConversionOptions
from webpeditor_app.core.converter.image_converter_service_abc import ImageConverterServiceABC
from webpeditor_app.core.logging import LoggerABC
from webpeditor_app.infrastructure.cloudinary import CloudinaryServiceABC
from webpeditor_app.infrastructure.cloudinary.models import UploadOptions
from webpeditor_app.models import ConvertedImageAsset

from webpeditor_app.utils.text_utils import replace_with_underscore


class ImageConverterService(ImageConverterServiceABC):
    @inject
    def __init__(
        self,
        cloudinary_service: CloudinaryServiceABC,
        image_file_utility_service: ImageFileUtilityServiceABC,
        logger: LoggerABC,
    ):
        self.__cloudinary_service: CloudinaryServiceABC = cloudinary_service
        self.__image_file_utility_service: ImageFileUtilityServiceABC = image_file_utility_service
        self.__logger: LoggerABC = logger

    def convert(self, request: ConversionRequest) -> ResultantValue[ConversionResponse]:
        converted_image_asset: Optional[ConvertedImageAsset] = ConvertedImageAsset.objects.filter(user_id=request.user_id).first()
        # Delete previous content if exist
        if converted_image_asset is not None:
            converted_image_asset.delete()
            self.__cloudinary_service.delete_converted_images(request.user_id)

        converted_images_list: list[ResultantValue[str]] = []

        with ThreadPoolExecutor() as executor:
            futures: list[Future[ResultantValue[str]]] = [
                executor.submit(self.__convert_internal, *image_asset_data)
                for image_asset_data in [
                    (
                        i + 1,
                        request.user_id,
                        image_file,
                        request.options,
                    )
                    for i, image_file in enumerate(request.images_files)
                ]
            ]

            for future in as_completed(futures):
                try:
                    result: ResultantValue[str] = future.result()
                    converted_images_list.append(result)
                except Exception as e:
                    self.__logger.log_exception(e, "An error occurred in a parallel task")
                    raise e

        return converted_images_list

    def __convert_internal(
        self,
        image_id: int,
        user_id: str,
        image_file: UploadedFile,
        options: ConversionOptions,
    ) -> ResultantValue[str]:
        new_filename: str = self.__create_new_filename(image_file, options=options)

        shorten_filename_resultant: ResultantValue[str] = self.__image_file_utility_service.shorten_filename(new_filename, max_filename_size=25)
        if not Resultant.is_successful(shorten_filename_resultant):
            return Resultant.from_failure(shorten_filename_resultant.failure())

        shorten_filename: str = shorten_filename_resultant.unwrap()

        convert_image_resultant: ResultantValue[tuple[ImageFile, Image.Image, BytesIO]] = self.__convert_image(image_file, options=options)

        if not Resultant.is_successful(convert_image_resultant):
            return Resultant.from_failure(convert_image_resultant.failure())

        original_image, converted_image, converted_image_buffer = convert_image_resultant.unwrap()

        # cloudinary_options: dict = {
        #     "folder": ,
        #     "use_filename": True,
        #     "unique_filename": True,
        #     "filename_override": new_filename,
        #     "overwrite": False,
        # }

        cloudinary_image: ResultantValue[CloudinaryImage] = self.__cloudinary_service.upload_image(
            converted_image_buffer,
            options=UploadOptions(
                folder_path=f"{user_id}/converted/",
                use_filename=True,
                unique_filename=True,
                filename_override=new_filename,
                overwrite=False,
            ),
        )

        # image_set = create_image_set(
        #     image_id,
        #     original_image,
        #     converted_image,
        #     converted_image_buffer,
        #     image_file,
        #     cloudinary_image.url,
        #     new_filename,
        #     shorten_filename_resultant,
        #     public_id,
        #     output_format,
        # )
        #
        # original_image_data = image_set.get("original_image_data")
        # converted_image_data = image_set.get("converted_image_data")
        #
        # original_image_file_size = original_image_data.get("image_file_size")  # pyright: ignore [reportAttributeAccessIssue, reportOptionalMemberAccess]
        # converted_image_file_size = converted_image_data.get("image_file_size")  # pyright: ignore [reportAttributeAccessIssue, reportOptionalMemberAccess]
        # original_image_exif_data = original_image_data.get("image_exif_data")  # pyright: ignore [reportAttributeAccessIssue, reportOptionalMemberAccess]
        # converted_image_exif_data = converted_image_data.get("image_exif_data")  # pyright: ignore [reportAttributeAccessIssue, reportOptionalMemberAccess]
        #
        # update_converted_image(user_id, request, image_set)

        # return (
        #     cloudinary_image.url,
        #     new_filename,
        #     public_id,
        #     shorten_filename_resultant,
        #     str(original_image.format).upper(),
        #     output_format.upper(),
        #     original_image_file_size,
        #     converted_image_file_size,
        #     str(original_image.mode),
        #     original_image_exif_data,
        #     str(converted_image.mode),
        #     converted_image_exif_data,
        # )

        return Resultant.success("")

    @staticmethod
    def __create_new_filename(image_file: UploadedFile, *, options: ConversionOptions) -> str:
        filename_without_extension: str = replace_with_underscore(image_file.name).rsplit(".", 1)[0]
        new_file_extension: str = options.output_format.lower()

        new_filename: str = f"webpeditor_{filename_without_extension}.{new_file_extension}"

        return new_filename

    def __convert_image(
        self,
        image_file: UploadedFile,
        *,
        options: ConversionOptions,
    ) -> ResultantValue[tuple[ImageFile, Image.Image, BytesIO]]:
        buffer: BytesIO = BytesIO()
        original_image: ImageFile = Image.open(image_file.file)

        exif_data: Exif = original_image.getexif()

        converted_image_resultant: ResultantValue[Image.Image] = self.__convert_color_mode_with_alpha_handling(
            original_image,
            output_format=options.output_format,
        )

        if not Resultant.is_successful(converted_image_resultant):
            return Resultant.from_failure(converted_image_resultant.failure())

        converted_image: Image.Image = converted_image_resultant.unwrap()

        match options.output_format:
            case ImageConverterSettings.OutputFormats.JPEG | ImageConverterSettings.OutputFormats.JPG:
                converted_image.save(
                    buffer,
                    format=ImageConverterSettings.OutputFormats.JPEG,
                    quality=options.quality,
                    subsampling=0 if options.quality == 100 else 2,
                    exif=exif_data,
                )
            case ImageConverterSettings.OutputFormats.TIFF:
                converted_image.save(
                    buffer,
                    format=ImageConverterSettings.OutputFormats.TIFF,
                    quality=options.quality,
                    exif=exif_data,
                    compression="jpeg",
                )
            case ImageConverterSettings.OutputFormats.BMP:
                converted_image.save(buffer, format=ImageConverterSettings.OutputFormats.BMP)
            case _:
                converted_image.save(
                    buffer,
                    format=options.output_format,
                    quality=options.quality,
                    exif=exif_data,
                )

        # Reset buffer pointer
        buffer.seek(0)

        return Resultant.success((original_image, converted_image, buffer))

    @staticmethod
    def __convert_color_mode_with_alpha_handling(original_image: ImageFile, *, output_format: str) -> ResultantValue[Image.Image]:
        image_format: Optional[str] = original_image.format

        if image_format is None:
            return Resultant.error("Invalid image format", error_code=ErrorCode.INTERNAL_SERVER_ERROR)

        if image_format.upper() not in ImageConverterSettings.OutputFormatsWithAlphaChannel:
            return Resultant.success(original_image.convert("RGB"))

        rgba_image: Image.Image = original_image.convert("RGBA")

        if output_format.upper() in ImageConverterSettings.OutputFormatsWithAlphaChannel:
            return Resultant.success(rgba_image)

        image_with_white_background: Image.Image = Image.new("RGB", rgba_image.size, (255, 255, 255))
        # Use the alpha channel as a mask
        image_with_white_background.paste(rgba_image, mask=rgba_image.split()[3])

        return Resultant.success(image_with_white_background)


# def update_converted_image(user_id: str, request: WSGIRequest, image_set: dict):
#     converted_image_query_set: QuerySet[ConvertedImageAsset] = ConvertedImageAsset.objects.filter(user_id=user_id)
#     converted_image: ConvertedImageAsset | None = converted_image_query_set.first()
#
#     if converted_image is None:
#         converted_image = ConvertedImageAsset(
#             user_id=user_id,
#             image_set=[image_set],
#             session_key=request.session.session_key,
#             session_key_expiration_date=request.session.get_expiry_date(),
#         )
#         converted_image.save()
#     else:
#         updated_image_set = copy(converted_image.image_data)
#         updated_image_set.append(image_set)
#         converted_image_query_set.update(image_set=updated_image_set)


# def create_image_set(
#     image_id: int,
#     pil_image: Image.Image,
#     pil_image_converted: Image.Image,
#     converted_image_buffer: BytesIO,
#     original_image_file: InMemoryUploadedFile,
#     cloudinary_image_url: str,
#     new_image_name: str,
#     new_image_name_shorter: str,
#     public_id: str,
#     output_format: str,
# ) -> dict[str, str | dict[str, str | Exif] | dict[str, str | Exif] | int]:
#     if original_image_file.file is None:
#         raise IOError("Failed to read the original image file.")
#
#     original_image_file_size: str = get_image_file_size(original_image_file.file)  # pyright: ignore [reportArgumentType]
#     converted_image_file_size: str = get_image_file_size(converted_image_buffer)
#
#     original_image_exif_data = get_image_info(original_image_file.file)[6]  # pyright: ignore [reportOptionalSubscript, reportArgumentType]
#     converted_image_exif_data = get_image_info(converted_image_buffer)[6]  # pyright: ignore [reportOptionalSubscript]
#
#     image_set: dict = {
#         "image_id": image_id,
#         "image_name_shorter": new_image_name_shorter,
#         "public_id": public_id,
#         "image_name": new_image_name,
#         "image_url": cloudinary_image_url,
#         "original_image_data": {
#             "content_type": f"image/{str(pil_image.format).lower()}",
#             "image_file_size": original_image_file_size,
#             "image_mode": str(pil_image.mode),
#             "image_exif_data": original_image_exif_data,
#         },
#         "converted_image_data": {
#             "content_type": f"image/{output_format.lower()}",
#             "image_file_size": converted_image_file_size,
#             "image_mode": str(pil_image_converted.mode),
#             "image_exif_data": converted_image_exif_data,
#         },
#     }
#
#     return image_set
