from datetime import datetime
from typing import Final, final

from expression import Option

from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, as_awaitable_result
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.infrastructure.database.models import AppUser


@final
class UserRepository(UserRepositoryABC):
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aget_or_create(
        self,
        session_key: str,
        session_key_expiration_date: datetime,
    ) -> ContextResult[AppUser]:
        try:
            app_user, _ = await AppUser.objects.aget_or_create(
                session_key=session_key,
                session_key_expiration_date=session_key_expiration_date,
            )
            message = f"User '{app_user.id}' with session key '{session_key}' and expiration date '{session_key_expiration_date}' has been created"
            self.__logger.debug(message)
            return ContextResult[AppUser].success(app_user)
        except Exception as exception:
            message = f"Failed to create User with session key '{session_key}' and expiration date '{session_key_expiration_date}'"
            self.__logger.exception(exception, message)
            return ContextResult[AppUser].failure(ErrorContext.server_error())

    @as_awaitable_result
    async def aget(self, user_id: str) -> ContextResult[AppUser]:
        app_user = await AppUser.objects.filter(id=user_id).afirst()
        result = Option.of_optional(app_user).to_result(ErrorContext.not_found(f"Unable to find current user '{user_id}'"))
        return ContextResult[AppUser].from_result(result)

    @as_awaitable_result
    async def aget_by_session_key(self, session_key: str) -> ContextResult[AppUser]:
        app_user = await AppUser.objects.filter(session_key=session_key).afirst()
        result = Option.of_optional(app_user).to_result(ErrorContext.not_found(f"Unable to find user with session key '{session_key}'"))
        return ContextResult[AppUser].from_result(result)
