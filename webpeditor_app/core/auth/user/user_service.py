import uuid

from django.core import signing
from injector import inject

from webpeditor_app.common.resultant import ResultantValue, Resultant, ErrorCode
from webpeditor_app.core.auth.user.user_service_abc import UserServiceABC
from webpeditor_app.core.logging import LoggerABC


class UserService(UserServiceABC):
    @inject
    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: LoggerABC = logger

    def create_signed_user_id(self) -> ResultantValue[str]:
        signed_user_id: str = signing.dumps(str(uuid.uuid4()))
        return Resultant.success(signed_user_id)

    def unsign_user_id(self, signed_user_id: str) -> ResultantValue[str]:
        try:
            unsigned_user_id: str = signing.loads(signed_user_id)
            return Resultant.success(unsigned_user_id)
        except Exception as e:
            self.__logger.log_exception_500(e)
            return Resultant.error("Failed to parse signed user ID", error_code=ErrorCode.INTERNAL_SERVER_ERROR)
