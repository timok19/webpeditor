from typing import Optional

from django.http.request import HttpRequest
from ninja.security import APIKeyHeader
from ninja_extra import NinjaExtraAPI

from webpeditor.settings import WEBPEDITOR_API_KEY, APP_VERSION, APP_VERBOSE_NAME
from webpeditor_app.controllers.image_converter_controller import ImageConverterController


# TODO: create a separate app for creating API keys (storing the database and hashing values)
class APIKey(APIKeyHeader):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        return key if key == WEBPEDITOR_API_KEY else None


webpeditor_api = NinjaExtraAPI(title=APP_VERBOSE_NAME, version=APP_VERSION, auth=APIKey())
webpeditor_api.register_controllers(ImageConverterController)  # pyright: ignore [reportUnknownMemberType]
