from abc import ABC, abstractmethod

from pydantic import HttpUrl

from webpeditor_app.core.result import ContextResult, as_awaitable_result


class FilesRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aupload_file(self, user_id: str, relative_path: str, content: bytes) -> ContextResult[HttpUrl]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_zip_folder(self, user_id: str) -> ContextResult[HttpUrl]: ...

    @abstractmethod
    @as_awaitable_result
    async def acleanup(self, user_id: str) -> ContextResult[None]: ...

    @staticmethod
    @abstractmethod
    def _get_root_folder(user_id: str) -> str: ...
