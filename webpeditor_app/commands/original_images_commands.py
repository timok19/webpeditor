import logging

from django.http import JsonResponse
from uuid import UUID

from webpeditor_app.database.models.original_image_model import OriginalImage
from webpeditor_app.services.external_api_services.cloudinary_service import (
    CloudinaryService,
)


class OriginalImagesCommands:
    @staticmethod
    async def get_all_original_images():
        original_images: list[OriginalImage] = await OriginalImage.find_all().to_list()
        if len(original_images) == 0:
            raise ValueError("Original images do not exist in db")

        return original_images

    @staticmethod
    async def get_original_image(user_id: UUID):
        original_image: OriginalImage | None = await OriginalImage.find_one(
            OriginalImage.item.user_id == user_id
        )

        return original_image if not None else None

    @classmethod
    async def delete_original_image(cls, user_id: UUID):
        original_image = await cls.get_original_image(user_id)
        if original_image is None:
            logging.info(
                f"Original image of user {user_id} not found. Deleting user's folder..."
            )
            CloudinaryService.delete_original_and_edited_images(user_id.__str__())
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
