from abc import ABC, abstractmethod
from typing import Union

from core.result import ContextResult


class FilenameServiceABC(ABC):
    @abstractmethod
    def normalize(self, filename: Union[str, bytes]) -> ContextResult[str]: ...

    @abstractmethod
    def trim(self, filename: Union[str, bytes], max_length: int) -> ContextResult[str]: ...

    @abstractmethod
    def get_basename(self, filename: Union[str, bytes]) -> ContextResult[str]: ...
