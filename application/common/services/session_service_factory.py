from typing import final, Final

from django.http import HttpRequest

from application.common.abc.signing_service_abc import SigningServiceABC
from application.common.services.session_service import SessionService
from core.abc.logger_abc import LoggerABC


@final
class SessionServiceFactory:
    def __init__(self, signing_service: SigningServiceABC, logger: LoggerABC) -> None:
        self.__signing_service: Final[SigningServiceABC] = signing_service
        self.__logger: Final[LoggerABC] = logger

    def create(self, http_request: HttpRequest) -> SessionService:
        return SessionService(http_request, self.__signing_service, self.__logger)
