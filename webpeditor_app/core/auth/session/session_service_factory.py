from injector import inject
from rest_framework.request import Request

from webpeditor_app.core.auth.session.session_service_factory_abc import SessionServiceFactoryABC
from webpeditor_app.core.auth.session.session_service import SessionService
from webpeditor_app.core.auth.user import UserServiceABC
from webpeditor_app.core.logging import LoggerABC
from webpeditor_app.infrastructure.cloudinary import CloudinaryServiceABC


class SessionServiceFactory(SessionServiceFactoryABC):
    @inject
    def __init__(
        self,
        user_service: UserServiceABC,
        cloudinary_service: CloudinaryServiceABC,
        logger: LoggerABC,
    ) -> None:
        self.__user_service: UserServiceABC = user_service
        self.__cloudinary_service: CloudinaryServiceABC = cloudinary_service
        self.__logger: LoggerABC = logger

    def create(self, request: Request) -> SessionService:
        return SessionService(request, self.__user_service, self.__cloudinary_service, self.__logger)
