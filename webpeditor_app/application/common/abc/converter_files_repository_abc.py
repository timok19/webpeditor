from abc import ABC, abstractmethod

from webpeditor_app.application.common.abc.files_repository_abc import FilesRepositoryABC
from webpeditor_app.core.result import ContextResult
from webpeditor_app.core.result.decorators import as_awaitable_result
from webpeditor_app.globals import Unit


class ConverterFilesRepositoryABC(FilesRepositoryABC, ABC):
    @abstractmethod
    @as_awaitable_result
    async def aupload_original(self, user_id: str, filename: str, content: bytes) -> ContextResult[str]: ...

    @abstractmethod
    @as_awaitable_result
    async def aupload_converted(self, user_id: str, filename: str, content: bytes) -> ContextResult[str]: ...

    @abstractmethod
    @as_awaitable_result
    async def acleanup(self, user_id: str) -> ContextResult[Unit]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_zip(self, user_id: str) -> ContextResult[str]: ...
