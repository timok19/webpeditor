from typing import IO, Any, Mapping, Optional, Sequence, Union

from httpx import QueryParams

FileContent = Union[IO[bytes], bytes, str]
FileTypes = Union[
    FileContent,
    tuple[Optional[str], FileContent],
    tuple[Optional[str], FileContent, Optional[str]],
    tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]
RequestFiles = Union[Mapping[str, FileTypes], Sequence[tuple[str, FileTypes]]]
PrimitiveData = Optional[Union[str, int, float, bool]]
QueryParamTypes = Union[
    QueryParams,
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    list[tuple[str, PrimitiveData]],
    tuple[tuple[str, PrimitiveData], ...],
    str,
    bytes,
]
RequestData = Mapping[str, Any]
