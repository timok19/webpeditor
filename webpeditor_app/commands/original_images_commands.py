import logging

from django.http import JsonResponse
from uuid import UUID

from webpeditor_app.database.models.original_image_model import OriginalImage
from webpeditor_app.services.other_services.cloudinary_service import (
    CloudinaryService,
)


class OriginalImagesCommands:
    def __init__(self, user_id: UUID):
        self.user_id = user_id

    @staticmethod
    async def create_original_image(original_image: OriginalImage):
        await OriginalImage.insert_one(original_image)

    @staticmethod
    async def get_all_original_images():
        original_images: list[OriginalImage] = await OriginalImage.find_all().to_list()
        if len(original_images) == 0:
            raise ValueError("Original images do not exist in db")

        return original_images

    async def get_original_image(self):
        original_image: OriginalImage | None = await OriginalImage.find_one(
            OriginalImage.image.user_id == self.user_id
        )

        return original_image if not None else None

    async def delete_original_image(self):
        original_image = await self.get_original_image()
        if original_image is None:
            logging.info(
                f"Original image of user {self.user_id} not found. Deleting user's folder..."
            )
            CloudinaryService.delete_original_and_edited_images(self.user_id.__str__())
        else:
            await original_image.delete()

        logging.info("Original image has been deleted")

        return JsonResponse(
            data={
                "success": True,
                "info": "Original and Edited images have been deleted in db",
            },
            status=200,
        )
