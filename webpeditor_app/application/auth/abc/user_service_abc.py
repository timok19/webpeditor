from abc import ABC, abstractmethod


from webpeditor_app.core.extensions.result_extensions import ContextResult


class UserServiceABC(ABC):
    @abstractmethod
    def sign_id(self, user_id: str) -> str: ...

    @abstractmethod
    def unsign_id(self, signed_user_id: str) -> ContextResult[str]: ...
