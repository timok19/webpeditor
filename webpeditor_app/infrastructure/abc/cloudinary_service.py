from abc import ABC, abstractmethod
from typing import Any, Callable


class CloudinaryServiceABC(ABC):
    @abstractmethod
    def delete_assets(self, user_id: str, filter_func: Callable[[dict[str, Any]], bool] | None = None) -> None: ...

    @abstractmethod
    def delete_user_assets_in_subfolder(self, user_id: str, subfolder: str) -> None: ...

    @abstractmethod
    def delete_user_folder(self, user_id: str) -> None: ...

    @abstractmethod
    def delete_all_folders(self) -> None: ...

    @abstractmethod
    def get_all_users_folders(self) -> list[str]: ...

    @abstractmethod
    def delete_original_and_edited_images(self, user_id: str) -> None: ...

    @abstractmethod
    def delete_converted_images(self, user_id: str) -> None: ...
