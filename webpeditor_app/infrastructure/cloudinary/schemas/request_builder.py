from http import HTTPMethod
from typing import Optional, Union, final, Iterable, AsyncIterable

from httpx import QueryParams
from pydantic import BaseModel, ConfigDict


@final
class Request[T: (BaseModel, None)](BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True, arbitrary_types_allowed=True)

    url: str
    method: HTTPMethod
    content: Optional[Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]] = None
    params: Optional[QueryParams] = None
    data: Optional[T] = None


class RequestBuilder[T: (BaseModel, None)]:
    def __init__(self, method: HTTPMethod, url: str) -> None:
        self.__url: str = url
        self.__method: HTTPMethod = method
        self.__content: Optional[Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]] = None
        self.__params: Optional[QueryParams] = None
        self.__data: Optional[T] = None

    def with_content(self, content: Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]) -> "RequestBuilder[T]":
        self.__content = content
        return self

    def with_params(self, params: QueryParams) -> "RequestBuilder[T]":
        self.__params = params
        return self

    def with_data(self, data: T) -> "RequestBuilder[T]":
        self.__data = data
        return self

    def build(self) -> Request[T]:
        return Request(
            url=self.__url,
            method=self.__method,
            content=self.__content,
            params=self.__params,
            data=self.__data,
        )
