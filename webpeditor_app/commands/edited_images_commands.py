from uuid import UUID

from webpeditor_app.database.models.edited_image_model import EditedImage


class EditedImagesCommands:
    def __init__(self, user_id: UUID):
        self.user_id = user_id

    @staticmethod
    async def get_all_edited_images():
        edited_images: list[EditedImage] = await EditedImage.find_all().to_list()
        if len(edited_images) == 0:
            raise ValueError("Edited images do not exist")

        return edited_images

    async def get_edited_image(self):
        edited_image: EditedImage | None = await EditedImage.find_one(
            EditedImage.image.user_id == self.user_id
        )

        return edited_image if not None else None
