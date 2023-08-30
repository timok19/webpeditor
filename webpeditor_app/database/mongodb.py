from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from webpeditor.settings import DATABASE_URL, DATABASE_NAME
from webpeditor_app.database.models.edited_image_model import EditedImage
from webpeditor_app.database.models.original_image_model import OriginalImage
from webpeditor_app.database.models.converted_image_model import ConvertedImage


class MongoDBHandler:
    mongodb_client = AsyncIOMotorClient(DATABASE_URL)
    mongodb = mongodb_client[DATABASE_NAME]

    @classmethod
    async def mongodb_init(cls):
        await init_beanie(
            cls.mongodb,
            document_models=[
                OriginalImage,
                EditedImage,
                ConvertedImage,
            ],
        )

    @classmethod
    async def mongodb_close(cls):
        cls.mongodb_client.close()