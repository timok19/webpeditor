import logging
from uuid import UUID, uuid4

from concurrent.futures import ThreadPoolExecutor, as_completed

from io import BytesIO
from typing import List, Tuple
from copy import copy

from PIL.Image import Image, open, new, Exif
from beanie.odm.operators.update.general import Set
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.asgi import ASGIRequest

from webpeditor_app.commands.converted_images_commands import ConvertedImagesCommands
from webpeditor_app.utils.text_utils import replace_with_underscore
from webpeditor_app.database.models.image_converter_models import (
    ConvertedImage,
    ImageSet,
    ImageData,
)
from webpeditor_app.services.external_api_services.cloudinary_service import (
    CloudinaryService,
)
from webpeditor_app.services.image_services.image_editor_service import (
    slice_image_name,
    get_image_info,
    get_image_file_size,
)
from webpeditor_app.services.image_services.types import (
    RGBImageFormat,
    RGBAImageFormat,
    AllowedImageFormats,
)


class ImageConverterService:
    MIN_QUALITY: int = 5
    MAX_QUALITY: int = 100
    SAFE_QUALITY: int = 95

    image: Image | None = None
    converted_image: Image | None = None
    exif_data: Exif | None = None

    def __init__(
        self,
        user_id: UUID,
        request: ASGIRequest,
        image_files: List[InMemoryUploadedFile],
        quality: int | None = 50,
        output_format: AllowedImageFormats | None = RGBAImageFormat.WEBP,
    ):
        self.user_id = user_id
        self.request = request
        self.image_files = image_files
        self.quality = quality
        self.output_format = output_format
        self.converted_images_commands = ConvertedImagesCommands(user_id)

    def convert_image(self, image_file: InMemoryUploadedFile) -> BytesIO:
        if self.MIN_QUALITY > self.quality > self.MAX_QUALITY:
            raise ValueError(
                f"Image quality cannot be less than {self.MIN_QUALITY} "
                f"and more than {self.MAX_QUALITY}"
            )

        image_buffer = BytesIO()

        self.image = open(image_file)
        self.exif_data = self.image.getexif()

        self.converted_image: Image = self.convert_color_mode(
            self.image.format,
            self.output_format,
        )

        match self.output_format:
            case RGBImageFormat.JPEG:
                self.converted_image.save(
                    fp=image_buffer,
                    format=self.output_format,
                    quality=self.quality,
                    subsampling=0 if self.quality == self.MAX_QUALITY else 2,
                    exif=self.exif_data,
                )
            case RGBImageFormat.TIFF:
                self.converted_image.save(
                    fp=image_buffer,
                    format=self.output_format,
                    quality=self.quality,
                    exif=self.exif_data,
                    compression="jpeg",
                )
            case RGBImageFormat.BMP:
                self.converted_image.save(
                    fp=image_buffer,
                    format=self.output_format,
                )
            case _:
                self.converted_image.save(
                    fp=image_buffer,
                    format=self.output_format,
                    quality=self.SAFE_QUALITY
                    if self.SAFE_QUALITY < self.quality <= self.MAX_QUALITY
                    else self.quality,
                    exif=self.exif_data,
                )
        # Set buffer pointer to start
        image_buffer.seek(0)

        return image_buffer

    async def update_converted_image(self, image_set: ImageSet):
        converted_image = await self.converted_images_commands.get_converted_image()

        if converted_image is None:
            await ConvertedImage.insert_one(
                ConvertedImage(
                    user_id=self.user_id,
                    image_set=[image_set],
                    session_key=self.request.session.session_key,
                    session_key_expiration_date=self.request.session.get_expiry_date(),
                )
            )
        else:
            updated_image_set = copy(converted_image.image_set)
            updated_image_set.append(image_set)
            await self.converted_images_commands.update_converted_image(
                values=Set({ConvertedImage.image_set: [updated_image_set]}),
            )

    def create_image_set(
        self,
        image_id: UUID,
        image_file: InMemoryUploadedFile,
        converted_image_buffer: BytesIO,
        cloudinary_image_url: str,
        new_image_name: str,
        new_short_image_name: str,
        public_id: str,
        output_format: AllowedImageFormats,
    ) -> ImageSet:
        original_image_exif_data = get_image_info(image_file.file)[6]
        converted_image_exif_data = get_image_info(converted_image_buffer)[6]

        return ImageSet(
            image_id=image_id,
            short_image_name=new_short_image_name,
            public_id=public_id,
            image_name=new_image_name,
            image_url=cloudinary_image_url,
            original_image_data=ImageData(
                content_type=f"image/{str(self.image.format).lower()}",
                format=str(self.image.format),
                file_size=get_image_file_size(image_file.file),
                color_mode=str(self.image.mode),
                exif_data=original_image_exif_data,
            ),
            converted_image_data=ImageData(
                content_type=f"image/{str(output_format.value)}",
                format=str(output_format.value),
                file_size=get_image_file_size(converted_image_buffer),
                color_mode=str(self.converted_image.mode),
                exif_data=converted_image_exif_data,
            ),
        )

    def convert_color_mode(
        self,
        input_format: AllowedImageFormats,
        output_format: AllowedImageFormats,
    ) -> Image:
        if input_format in (image_format.value for image_format in RGBImageFormat):
            return self.image.convert("RGB")

        rgba_image = self.image.convert("RGBA")

        if output_format == RGBAImageFormat:
            return rgba_image

        image_with_white_bg = new(
            mode="RGB",
            size=rgba_image.size,
            color=(255, 255, 255),
        )

        # Use the alpha channel as a mask
        image_with_white_bg.paste(
            im=rgba_image,
            mask=rgba_image.split()[3],
        )

        return image_with_white_bg

    async def convert_and_save_image(
        self,
        arguments: Tuple[UUID, InMemoryUploadedFile],
    ):
        image_id, image_file = arguments

        new_image_name: str = (
            f"webpeditor_"
            f'{replace_with_underscore(image_file.name).rsplit(".", 1)[0]}'
            f".{self.output_format.value}"
        )
        new_short_image_name: str = slice_image_name(new_image_name, 25)

        try:
            converted_image_buffer: BytesIO = self.convert_image(image_file)

            cloudinary_image = CloudinaryService.upload_image(
                file=converted_image_buffer,
                parameters={
                    "folder": f"{self.user_id.__str__()}/converted/",
                    "use_filename": True,
                    "unique_filename": True,
                    "filename_override": new_image_name,
                    "overwrite": False,
                },
            )

            image_set: ImageSet = self.create_image_set(
                image_id=image_id,
                image_file=image_file,
                converted_image_buffer=converted_image_buffer,
                cloudinary_image_url=cloudinary_image.url,
                new_image_name=new_image_name,
                new_short_image_name=new_short_image_name,
                public_id=str(cloudinary_image.public_id),
                output_format=self.output_format,
            )
            await self.update_converted_image(image_set)

            return image_set

        except Exception as e:
            raise e

    async def run_conversion_task(self):
        converted_images = []
        converted_image = await self.converted_images_commands.get_converted_image()

        if converted_image:
            await converted_image.delete()
            CloudinaryService.delete_converted_images(
                f"{self.user_id.__str__()}/converted/"
            )

        with ThreadPoolExecutor() as executor:
            args_list = [(uuid4(), image_file) for image_file in self.image_files]

            futures = [
                executor.submit(self.convert_and_save_image, arguments)
                for arguments in args_list
            ]

            for future in as_completed(futures):
                try:
                    converted_images.append(future.result())
                except Exception as e:
                    logging.error(f"An error occurred in a parallel task: {e}")
                    raise e

            return converted_images
