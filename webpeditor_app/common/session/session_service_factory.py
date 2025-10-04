from typing import final, Final

from django.http import HttpRequest

from webpeditor_app.common.abc.user_service_abc import UserServiceABC
from webpeditor_app.common.session.session_service import SessionService
from webpeditor_app.core.abc.logger_abc import LoggerABC


@final
class SessionServiceFactory:
    def __init__(self, user_service: UserServiceABC, logger: LoggerABC) -> None:
        self.__user_service: Final[UserServiceABC] = user_service
        self.__logger: Final[LoggerABC] = logger

    def create(self, request: HttpRequest) -> SessionService:
        return SessionService(request, self.__user_service, self.__logger)
