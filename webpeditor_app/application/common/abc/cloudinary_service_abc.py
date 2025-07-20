from abc import ABC, abstractmethod

from webpeditor_app.core.result import ContextResult, as_awaitable_result
from webpeditor_app.globals import Unit


class CloudinaryServiceABC(ABC):
    @abstractmethod
    @as_awaitable_result
    async def aupload_file(self, public_id: str, file_content: bytes) -> ContextResult[str]: ...

    @abstractmethod
    @as_awaitable_result
    async def adelete_folder_recursively(self, folder_path: str) -> ContextResult[Unit]: ...

    @abstractmethod
    async def adelete_all_folders(self) -> None: ...

    @abstractmethod
    def get_all_users_folders(self) -> list[str]: ...
