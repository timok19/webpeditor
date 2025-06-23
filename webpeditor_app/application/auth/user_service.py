from typing import Final, final

from django.core import signing

from webpeditor import settings
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext


@final
class UserService(UserServiceABC):
    def __init__(self, logger: WebPEditorLoggerABC) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = logger

    def sign_id(self, user_id: str) -> str:
        return signing.dumps(user_id, salt=settings.WEBPEDITOR_SALT_KEY)

    def unsign_id(self, signed_user_id: str) -> ContextResult[str]:
        try:
            return ContextResult[str].success(
                signing.loads(
                    signed_user_id,
                    salt=settings.WEBPEDITOR_SALT_KEY,
                    max_age=settings.SESSION_COOKIE_AGE,
                )
            )
        except Exception as exception:
            self.__logger.log_exception(exception, f"Invalid signed User ID: {signed_user_id}")
            return ContextResult[str].failure(ErrorContext.bad_request())
