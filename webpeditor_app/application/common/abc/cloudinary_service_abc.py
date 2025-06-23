from abc import ABC, abstractmethod

from webpeditor_app.core.result import ContextResult, acontext_result
from webpeditor_app.globals import Unit


class CloudinaryServiceABC(ABC):
    @abstractmethod
    @acontext_result
    async def aupload_file(self, public_id: str, file_content: bytes) -> ContextResult[str]: ...

    @abstractmethod
    @acontext_result
    async def adelete_folder_recursively(self, user_id: str, relative_folder_path: str) -> ContextResult[Unit]: ...

    @abstractmethod
    async def adelete_all_folders(self) -> None: ...

    @abstractmethod
    def get_all_users_folders(self) -> list[str]: ...
