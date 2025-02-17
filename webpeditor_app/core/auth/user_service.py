from typing import final
from django.core import signing
from returns.pipeline import is_successful
from returns.result import Failure, Success, attempt, Result

from webpeditor_app.common.result_extensions import FailureContext, ValueResult
from webpeditor_app.core.abc.user_service import UserServiceABC


@final
class UserService(UserServiceABC):
    def sign_id(self, user_id: str) -> str:
        return signing.dumps(user_id)

    def unsign_id(self, signed_user_id: str) -> ValueResult[str]:
        @attempt
        def __get_unsigned_id(value: str) -> str:
            return signing.loads(value)

        unsigned_id_result: Result[str, str] = __get_unsigned_id(signed_user_id)

        if not is_successful(unsigned_id_result):
            return Failure(
                FailureContext(
                    message=f"Invalid signed User ID: {unsigned_id_result.failure()}",
                    error_code=FailureContext.ErrorCode.BAD_REQUEST,
                )
            )

        return Success(unsigned_id_result.unwrap())
