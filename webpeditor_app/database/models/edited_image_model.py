from uuid import UUID

from beanie import Document
from pydantic import Field

from webpeditor_app.database.models.original_image_model import Image


class EditedImage(Document):
    item: Image
    original_image_id: UUID = Field(...)
