from ninja_extra import NinjaExtraAPI

from api.authentication.authenticator import APIKeyAuthenticator
from converter.api.converter_controller import ConverterController
from webpeditor import settings

api = NinjaExtraAPI(title=settings.APP_VERBOSE_NAME, version=settings.APP_VERSION, auth=APIKeyAuthenticator())
api.register_controllers(ConverterController)  # pyright: ignore
