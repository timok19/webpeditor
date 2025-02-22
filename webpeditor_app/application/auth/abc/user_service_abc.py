from abc import ABC, abstractmethod


from webpeditor_app.core.based_result import BasedResultOutput


class UserServiceABC(ABC):
    @abstractmethod
    def sign_id(self, user_id: str) -> str: ...

    @abstractmethod
    def unsign_id(self, signed_user_id: str) -> BasedResultOutput[str]: ...
