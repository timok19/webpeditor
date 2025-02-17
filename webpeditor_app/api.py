from typing import Optional

from django.http.request import HttpRequest
from ninja.security import APIKeyHeader
from ninja_extra import NinjaExtraAPI

from webpeditor.settings import WEBPEDITOR_API_KEY
from webpeditor_app.controllers.image_converter_controller import ImageConverterController


class APIKey(APIKeyHeader):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[str]:
        return key if key == WEBPEDITOR_API_KEY else None


webpeditor_api: NinjaExtraAPI = NinjaExtraAPI(title="WebP Editor API", version="1.1.0", auth=APIKey())
webpeditor_api.register_controllers(ImageConverterController)
