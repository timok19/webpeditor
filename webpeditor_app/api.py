from typing import Optional

from django.http.request import HttpRequest
from ninja.security import APIKeyHeader
from ninja_extra import NinjaExtraAPI

from webpeditor import settings
from webpeditor_app.controllers.image_converter_controller import ImageConverterController


# TODO: create a separate app for creating API keys (storing the database and hashing values)
class APIKey(APIKeyHeader):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        return key if key == settings.WEBPEDITOR_API_KEY else None


webpeditor_api = NinjaExtraAPI(title=settings.APP_VERBOSE_NAME, version=settings.APP_VERSION, auth=APIKey())
webpeditor_api.register_controllers(ImageConverterController)  # pyright: ignore
