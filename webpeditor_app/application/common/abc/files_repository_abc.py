from abc import ABC, abstractmethod

from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.types import Unit


class FilesRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aupload(self, user_id: str, relative_path: str, content: bytes) -> ContextResult[str]: ...

    @abstractmethod
    @as_awaitable_result
    async def azip_folder(self, user_id: str, relative_path: str) -> ContextResult[str]: ...

    @abstractmethod
    @as_awaitable_result
    async def acleanup(self, user_id: str) -> ContextResult[Unit]: ...

    @staticmethod
    @abstractmethod
    def _get_root_path(user_id: str) -> str: ...
