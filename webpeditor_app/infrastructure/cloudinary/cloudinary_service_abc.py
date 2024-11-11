from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Callable

from cloudinary import CloudinaryImage

from webpeditor_app.common.resultant import ResultantValue
from webpeditor_app.infrastructure.cloudinary.models import UploadOptions


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

    @abstractmethod
    def upload_image(self, file_buffer: BytesIO, *, options: UploadOptions) -> ResultantValue[CloudinaryImage]: ...
