from datetime import datetime
from typing import Final, final

from expression import Option

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.core.context_result import AwaitableContextResult, ContextResult, ErrorContext


@final
class UserRepository(UserRepositoryABC):
    def __init__(self, logger: WebPEditorLoggerABC) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = logger

    def acreate_user(self, session_key: str, session_key_expiration_date: datetime) -> AwaitableContextResult[AppUser]:
        async def acreate_user() -> ContextResult[AppUser]:
            try:
                user = await AppUser.objects.acreate(
                    session_key=session_key,
                    session_key_expiration_date=session_key_expiration_date,
                )
                return ContextResult[AppUser].success(user)
            except Exception as exception:
                message = f"Failed to create user with session key '{session_key}' and expiration date '{session_key_expiration_date}'"
                self.__logger.log_exception(exception, message)
                return ContextResult[AppUser].failure(ErrorContext.server_error())

        return AwaitableContextResult(acreate_user())

    def aget_user(self, user_id: str) -> AwaitableContextResult[AppUser]:
        async def aget_user() -> ContextResult[AppUser]:
            return ContextResult[AppUser].from_result(
                Option.of_optional(await AppUser.objects.filter(id=user_id).afirst()).to_result(
                    ErrorContext.not_found(f"Unable to find current user '{user_id}'")
                )
            )

        return AwaitableContextResult(aget_user())
