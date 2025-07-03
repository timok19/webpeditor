import hashlib
from datetime import UTC, datetime
from http import HTTPMethod
from typing import IO, Any, Final, Mapping, MutableMapping, Optional, Sequence, Union, final

from httpx import AsyncClient, BasicAuth, QueryParams
from pydantic import BaseModel

from webpeditor import settings
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, acontext_result
from webpeditor_app.globals import Unit
from webpeditor_app.infrastructure.cloudinary.schemas import (
    DeleteResourceResponse,
    GetResourcesResponse,
    UploadFileResponse,
)

_FileContent = Union[IO[bytes], bytes, str]
_FileTypes = Union[
    _FileContent,
    tuple[Optional[str], _FileContent],
    tuple[Optional[str], _FileContent, Optional[str]],
    tuple[Optional[str], _FileContent, Optional[str], Mapping[str, str]],
]
_RequestFiles = Union[Mapping[str, _FileTypes], Sequence[tuple[str, _FileTypes]]]
_PrimitiveData = Optional[Union[str, int, float, bool]]
_QueryParamTypes = Union[
    QueryParams,
    Mapping[str, Union[_PrimitiveData, Sequence[_PrimitiveData]]],
    list[tuple[str, _PrimitiveData]],
    tuple[tuple[str, _PrimitiveData], ...],
    str,
    bytes,
]
_RequestData = Mapping[str, Any]


@final
class CloudinaryClient:
    def __init__(self, logger: LoggerABC) -> None:
        self.__max_results: Final[int] = 500
        self.__logger: Final[LoggerABC] = logger

    @acontext_result
    async def aupload_file(self, public_id: str, file_content: bytes) -> ContextResult[UploadFileResponse]:
        return await self.__asend_request(
            HTTPMethod.POST,
            "image/upload",
            data=self.__create_form_data({"public_id": public_id}),
            files={"file": file_content},
            response_type=UploadFileResponse,
        )

    @acontext_result
    async def aget_files(self, user_id: str, relative_folder_path: str) -> ContextResult[GetResourcesResponse]:
        return await self.__asend_request(
            HTTPMethod.GET,
            "resources/image/upload",
            query_params={"prefix": f"{user_id}/{relative_folder_path}", "max_results": self.__max_results},
            response_type=GetResourcesResponse,
        )

    @acontext_result
    async def adelete_folder_recursively(self, folder_path: str) -> ContextResult[DeleteResourceResponse]:
        return await self.__asend_request(
            HTTPMethod.DELETE,
            "resources/image/upload",
            query_params={"prefix": folder_path},
            response_type=DeleteResourceResponse,
        )

    def __create_form_data(self, params: MutableMapping[str, str]) -> Mapping[str, str]:
        # Add api_key and timestamp if not present
        if "api_key" not in params.keys():
            params["api_key"] = settings.CLOUDINARY_API_KEY
        if "timestamp" not in params.keys():
            params["timestamp"] = str(int(datetime.now(UTC).timestamp()))

        params["signature"] = self.__generate_signature(params)
        return params

    @staticmethod
    def __generate_signature(params: MutableMapping[str, str]) -> str:
        # Remove file, cloud_name, resource_type, and api_key if present
        data_to_sign = {k: v for k, v in params.items() if k not in ["file", "cloud_name", "resource_type", "api_key"]}
        # Sort parameters alphabetically
        sorted_data = sorted(data_to_sign.items())
        # Create the serialized string
        serialized = "&".join(f"{k}={v}" for k, v in sorted_data)
        # Append API secret
        to_sign = serialized + settings.CLOUDINARY_API_SECRET
        # Create SHA-1 hash
        return hashlib.sha1(to_sign.encode()).hexdigest()

    @acontext_result
    async def __asend_request[TResponse: BaseModel](
        self,
        method: HTTPMethod,
        url: str,
        *,
        query_params: Optional[_QueryParamTypes] = None,
        data: Optional[_RequestData] = None,
        files: Optional[_RequestFiles] = None,
        response_type: type[TResponse],
    ) -> ContextResult[TResponse]:
        async with self.__get_client() as client:
            response = await client.request(method, url, params=query_params, data=data, files=files)

            if response.is_error:
                message = f"Unexpected Cloudinary error occurred when calling {method} {response.url} {response.text}"
                self.__logger.log_error(message)
                return ContextResult[TResponse].failure(ErrorContext.server_error())

            if response_type is Unit:
                return ContextResult[TResponse].success(response_type())

            return ContextResult[TResponse].success(response_type.model_validate(response.json()))

    @staticmethod
    def __get_client() -> AsyncClient:
        return AsyncClient(
            base_url=f"{settings.CLOUDINARY_BASE_URL}/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/",
            auth=BasicAuth(
                username=settings.CLOUDINARY_API_KEY,
                password=settings.CLOUDINARY_API_SECRET,
            ),
        )
