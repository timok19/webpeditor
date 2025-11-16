from typing import Union

from django.urls import URLPattern, URLResolver, path
from ninja_extra import NinjaExtraAPI

from api.authenticator import APIKeyAuthenticator
from api.controllers.converter_controller import ConverterController
from webpeditor import settings

api = NinjaExtraAPI(title=settings.APP_VERBOSE_NAME, version=settings.APP_VERSION, auth=APIKeyAuthenticator())
api.register_controllers(ConverterController)  # pyright: ignore

urlpatterns: list[Union[URLResolver, URLPattern]] = [path("", api.urls)]
