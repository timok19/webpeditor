from datetime import datetime
from typing import Final, final

from expression import Option

from webpeditor_app.core.abc.webpeditor_logger_abc import WebPEditorLoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, acontext_result
from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.models.app_user import AppUser


@final
class UserRepository(UserRepositoryABC):
    def __init__(self, logger: WebPEditorLoggerABC) -> None:
        self.__logger: Final[WebPEditorLoggerABC] = logger

    @acontext_result
    async def aget_or_create_user(
        self,
        session_key: str,
        session_key_expiration_date: datetime,
    ) -> ContextResult[AppUser]:
        try:
            app_user, exists = await AppUser.objects.aget_or_create(
                session_key=session_key,
                session_key_expiration_date=session_key_expiration_date,
            )
            self.__logger.log_debug(
                f"User '{app_user.id}' {'already exists' if exists else 'has been created'} "
                + f"with session key '{session_key}' and expiration date '{session_key_expiration_date}'"
            )
            return ContextResult[AppUser].success(app_user)
        except Exception as exception:
            message = f"Failed to create user with session key '{session_key}' and expiration date '{session_key_expiration_date}'"
            self.__logger.log_exception(exception, message)
            return ContextResult[AppUser].failure(ErrorContext.server_error())

    @acontext_result
    async def aget_user(self, user_id: str) -> ContextResult[AppUser]:
        app_user = await AppUser.objects.filter(id=user_id).afirst()
        result = Option.of_optional(app_user).to_result(
            ErrorContext.not_found(f"Unable to find current user '{user_id}'")
        )
        return ContextResult[AppUser].from_result(result)

    @acontext_result
    async def aget_user_by_session_key(self, session_key: str) -> ContextResult[AppUser]:
        app_user = await AppUser.objects.filter(session_key=session_key).afirst()
        result = Option.of_optional(app_user).to_result(
            ErrorContext.not_found(f"Unable to find user with session key '{session_key}'")
        )
        return ContextResult[AppUser].from_result(result)
