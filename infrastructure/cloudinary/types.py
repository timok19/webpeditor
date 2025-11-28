from typing import IO, Any, Mapping, Optional, Sequence, Union, MutableMapping

from httpx import QueryParams

type FileContent = Union[IO[bytes], bytes, str]
type FileTypes = Union[
    FileContent,
    tuple[Optional[str], FileContent],
    tuple[Optional[str], FileContent, Optional[str]],
    tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]
type RequestFiles = Union[Mapping[str, FileTypes], Sequence[tuple[str, FileTypes]]]
type PrimitiveData = Optional[Union[str, int, float, bool]]
type QueryParamTypes = Union[
    QueryParams,
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    list[tuple[str, PrimitiveData]],
    tuple[tuple[str, PrimitiveData], ...],
    str,
    bytes,
]
type RequestData = MutableMapping[str, Any]
