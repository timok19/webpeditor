from abc import ABC, abstractmethod

from pydantic import HttpUrl

from core.result import ContextResult, as_awaitable_result
from infrastructure.cloudinary.models import GetFilesResponse
from infrastructure.repositories.converter_files.models import UploadFileParams


class FilesRepositoryABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aupload_file(self, user_id: str, *, params: UploadFileParams) -> ContextResult[HttpUrl]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_zip(self, user_id: str, relative_folder_path: str) -> ContextResult[HttpUrl]: ...

    @abstractmethod
    @as_awaitable_result
    async def adelete_files(self, user_id: str, relative_folder_path: str) -> ContextResult[None]: ...

    @abstractmethod
    @as_awaitable_result
    async def aget_files(self, user_id: str, relative_folder_path: str) -> ContextResult[GetFilesResponse]: ...

    @staticmethod
    @abstractmethod
    def _get_root_folder_path(user_id: str) -> str: ...
