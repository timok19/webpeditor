from injector import Module, Binder, threadlocal, singleton

from webpeditor_app.core.auth.session.session_service_factory import SessionServiceFactory
from webpeditor_app.core.auth.session.session_service_factory_abc import SessionServiceFactoryABC
from webpeditor_app.core.auth.user.user_service import UserService
from webpeditor_app.core.auth.user.user_service_abc import UserServiceABC
from webpeditor_app.core.converter.image_converter_service import ImageConverterService
from webpeditor_app.core.converter.image_converter_service_abc import ImageConverterServiceABC
from webpeditor_app.core.logging.logger import Logger
from webpeditor_app.core.logging.logger_abc import LoggerABC


class DiModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(LoggerABC, to=Logger, scope=singleton)
        binder.bind(UserServiceABC, to=UserService, scope=threadlocal)
        binder.bind(SessionServiceFactoryABC, to=SessionServiceFactory, scope=threadlocal)
        binder.bind(ImageConverterServiceABC, to=ImageConverterService, scope=threadlocal)
