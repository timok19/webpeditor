from uuid import UUID

from beanie import Document
from pydantic import Field, BaseConfig

from webpeditor_app.database.models.original_image_model import ImageModel


class EditedImage(Document):
    image: ImageModel
    original_image_id: UUID = Field(...)

    class Config(BaseConfig):
        validate_all = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
