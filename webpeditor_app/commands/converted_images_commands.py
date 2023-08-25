import logging
from uuid import UUID

from django.http import JsonResponse

from webpeditor_app.models.database.models import ConvertedImage
from webpeditor_app.services.external_api_services.cloudinary_service import (
    CloudinaryService,
)


class ConvertedImagesCommands:
    logging.basicConfig(level=logging.INFO)

    @staticmethod
    async def get_all_converted_images():
        converted_images: list[
            ConvertedImage
        ] = await ConvertedImage.find_all().to_list()

        if len(converted_images) == 0:
            raise ValueError("Converted images do not exist in db")

        return converted_images

    @staticmethod
    async def get_converted_image(user_id: UUID):
        converted_image = await ConvertedImage.find_one(
            ConvertedImage.user_id == user_id
        )

        return converted_image if not None else None

    @classmethod
    async def delete_converted_image_in_db(cls, user_id: UUID) -> JsonResponse:
        converted_image: ConvertedImage | None = await cls.get_converted_image(user_id)
        if converted_image is None:
            logging.info(
                "No converted image was found in db. Deleting user's folder..."
            )
            CloudinaryService.delete_converted_images(user_id.__str__())
        else:
            await converted_image.delete()

        logging.info("Converted image has been deleted in db")

        return JsonResponse(
            data={
                "success": True,
                "info": "Converted image has been deleted in db",
            },
            status=200,
        )
