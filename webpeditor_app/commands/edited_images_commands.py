from uuid import UUID

from webpeditor_app.database.models.image_editor_models import EditedImage


class EditedImagesCommands:
    @staticmethod
    async def get_all_edited_images():
        edited_images: list[EditedImage] = await EditedImage.find_all().to_list()
        if len(edited_images) == 0:
            raise ValueError("Edited images do not exist")

        return edited_images

    @staticmethod
    async def get_edited_image(user_id: UUID):
        edited_image: EditedImage | None = await EditedImage.find_one(
            EditedImage.item.user_id == user_id
        )

        return edited_image if not None else None
