from abc import ABC, abstractmethod

from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.globals import Unit


class FilesRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def acleanup(self, user_id: str) -> ContextResult[Unit]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_zip(self, user_id: str) -> ContextResult[str]: ...

    @staticmethod
    @abstractmethod
    def _get_root_path(user_id: str) -> str: ...
