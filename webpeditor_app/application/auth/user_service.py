from typing import final
from django.core import signing
from returns.result import attempt

from webpeditor_app.core.extensions.result_extensions import FailureContext, ContextResult
from webpeditor_app.application.auth.abc.user_service_abc import UserServiceABC


@final
class UserService(UserServiceABC):
    def sign_id(self, user_id: str) -> str:
        return signing.dumps(user_id)

    def unsign_id(self, signed_user_id: str) -> ContextResult[str]:
        return self.__get_unsigned_id(signed_user_id).alt(
            lambda invalid_user_id: FailureContext(
                error_code=FailureContext.ErrorCode.BAD_REQUEST,
                message=f"Invalid signed User ID: {invalid_user_id}",
            )
        )

    @staticmethod
    @attempt
    def __get_unsigned_id(value: str) -> str:
        return signing.loads(value)
