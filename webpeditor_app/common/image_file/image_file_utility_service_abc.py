from abc import ABC, abstractmethod
from io import BytesIO

from webpeditor_app.common.image_file.models import ImageFileInfo
from webpeditor_app.common.resultant import ResultantValue


class ImageFileUtilityServiceABC(ABC):
    @abstractmethod
    def file_base64_to_bytes(self, file_base64: str) -> ResultantValue[bytes]: ...

    @abstractmethod
    def shorten_filename(self, filename: str, *, max_filename_size: int) -> ResultantValue[str]: ...

    @abstractmethod
    def get_file_extension(self, filename: str) -> str: ...

    @abstractmethod
    def get_file_basename(self, filename: str) -> str: ...

    @abstractmethod
    def get_bytes_from_file_url(self, file_url: str) -> ResultantValue[bytes]: ...

    @abstractmethod
    def get_file_info(self, file_buffer: BytesIO) -> ResultantValue[ImageFileInfo]: ...
