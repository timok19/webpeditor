from typing import Final, final

from django.core import signing

from webpeditor import settings
from application.common.abc.user_service_abc import UserServiceABC
from core.abc.logger_abc import LoggerABC
from core.result import ContextResult, ErrorContext


@final
class UserService(UserServiceABC):
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

    def sign_id(self, user_id: str) -> str:
        return signing.dumps(user_id, salt=settings.WEBPEDITOR_SALT_KEY, compress=True)

    def unsign_id(self, signed_user_id: str) -> ContextResult[str]:
        try:
            return ContextResult[str].success(signing.loads(signed_user_id, salt=settings.WEBPEDITOR_SALT_KEY))
        except Exception as exception:
            message = f"Invalid signed User ID: {signed_user_id}"
            self.__logger.exception(exception, message)
            return ContextResult[str].failure(ErrorContext.bad_request(message))
