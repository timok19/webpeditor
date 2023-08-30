import logging
from uuid import UUID

from beanie.odm.operators.update.general import Set
from django.http import JsonResponse

from webpeditor_app.database.models.image_converter_models import ConvertedImage
from webpeditor_app.services.external_api_services.cloudinary_service import (
    CloudinaryService,
)


class ConvertedImagesCommands:
    logging.basicConfig(level=logging.INFO)

    def __init__(self, user_id: UUID):
        self.user_id = user_id

    @staticmethod
    async def get_all_converted_images():
        converted_images: list[
            ConvertedImage
        ] = await ConvertedImage.find_all().to_list()

        if len(converted_images) == 0:
            raise ValueError("Converted images do not exist in db")

        return converted_images

    async def get_converted_image(self):
        converted_image = await ConvertedImage.find_one(
            ConvertedImage.user_id == self.user_id
        )

        return converted_image if not None else None

    async def update_converted_image(self, values: Set):
        converted_image = await self.get_converted_image()
        await converted_image.update(values)

    async def delete_converted_image_in_db(self) -> JsonResponse:
        converted_image: ConvertedImage | None = await self.get_converted_image()
        if converted_image is None:
            logging.info(
                "No converted image was found in db. Deleting user's folder..."
            )
            CloudinaryService.delete_converted_images(self.user_id.__str__())
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
