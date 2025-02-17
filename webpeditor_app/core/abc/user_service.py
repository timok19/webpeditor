from abc import ABC, abstractmethod


from webpeditor_app.common.result_extensions import ValueResult


class UserServiceABC(ABC):
    @abstractmethod
    def sign_id(self, user_id: str) -> str: ...

    @abstractmethod
    def unsign_id(self, signed_user_id: str) -> ValueResult[str]: ...
