from typing import final, Final
from django.core import signing
from expression import Failure, Success, Try

from webpeditor import settings
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC
from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.context_result import ContextResult, ErrorContext


@final
class UserService(UserServiceABC):
    def __init__(self) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__logger: Final[WebPEditorLoggerABC] = DiContainer.get_dependency(WebPEditorLoggerABC)

    def sign_id(self, user_id: str) -> str:
        return signing.dumps(user_id, salt=settings.WEBPEDITOR_SALT_KEY)

    def unsign_id(self, signed_user_id: str) -> ContextResult[str]:
        return ContextResult[str].from_result(
            self.__get_unsigned_id(signed_user_id)
            .map_error(lambda exc: self.__logger.log_exception(exc, f"Invalid signed User ID: {signed_user_id}"))
            .map_error(lambda _: ErrorContext.bad_request())
        )

    @staticmethod
    def __get_unsigned_id(value: str) -> Try[str]:
        try:
            return Success(signing.loads(value, salt=settings.WEBPEDITOR_SALT_KEY))
        except signing.BadSignature as bad_signature:
            return Failure(bad_signature)
