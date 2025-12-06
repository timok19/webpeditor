from typing import Any, Final, final

from django.core import signing

from application.common.abc.signing_service_abc import SigningServiceABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext
from webpeditor import settings


@final
class SigningService(SigningServiceABC):
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

    def sign(self, value: Any) -> str:
        return signing.dumps(value, salt=settings.WEBPEDITOR_SALT_KEY, compress=True)

    def unsign(self, signed_value: str) -> ContextResult[str]:
        try:
            return ContextResult[str].success(signing.loads(signed_value, salt=settings.WEBPEDITOR_SALT_KEY))
        except Exception as exception:
            message = f"Invalid signed value: {signed_value}"
            self.__logger.exception(exception, message)
            return ContextResult[str].failure(ErrorContext.bad_request(message))
