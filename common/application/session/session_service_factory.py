from typing import final, Final

from django.http import HttpRequest

from common.application.abc.user_service_abc import UserServiceABC
from common.application.session.session_service import SessionService
from common.core.abc.logger_abc import LoggerABC


@final
class SessionServiceFactory:
    def __init__(self, user_service: UserServiceABC, logger: LoggerABC) -> None:
        self.__user_service: Final[UserServiceABC] = user_service
        self.__logger: Final[LoggerABC] = logger

    def create(self, http_request: HttpRequest) -> SessionService:
        return SessionService(http_request, self.__user_service, self.__logger)
