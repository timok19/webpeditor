from typing import final

from expression import Option

from webpeditor_app.infrastructure.abc.user_repository_abc import UserRepositoryABC
from webpeditor_app.models.app_user import AppUser
from webpeditor_app.core.context_result import AwaitableContextResult, ContextResult, ErrorContext


@final
class UserRepository(UserRepositoryABC):
    def get_user_async(self, user_id: str) -> AwaitableContextResult[AppUser]:
        return AwaitableContextResult(self.__get_user_async(user_id))

    @staticmethod
    async def __get_user_async(user_id: str) -> ContextResult[AppUser]:
        user = await AppUser.objects.filter(id=user_id).afirst()
        message = f"Unable to find current user '{user_id}'"
        result = Option.of_optional(user).to_result(ErrorContext.not_found(message))
        return ContextResult[AppUser].from_result(result)
