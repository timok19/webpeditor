from abc import ABC, abstractmethod

from webpeditor_app.common.resultant import ResultantValue


class UserServiceABC(ABC):
    @abstractmethod
    def create_signed_user_id(self) -> ResultantValue[str]: ...

    @abstractmethod
    def unsign_user_id(self, signed_user_id: str) -> ResultantValue[str]: ...
