import hashlib
from datetime import datetime, timezone
from http import HTTPMethod
from typing import Final, MutableMapping, Optional, final, Any

from httpx import AsyncClient, BasicAuth
from pydantic import BaseModel

from webpeditor import settings
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, as_awaitable_result
from webpeditor_app.infrastructure.cloudinary.schemas import (
    DeleteResourceResponse,
    GetResourcesResponse,
    UploadFileResponse,
)
from webpeditor_app.infrastructure.cloudinary.schemas.archive import GenerateArchiveResponse
from webpeditor_app.infrastructure.cloudinary.types import QueryParamTypes, RequestData, RequestFiles


@final
class CloudinaryClient:
    def __init__(self, logger: LoggerABC) -> None:
        self.__max_results: Final[int] = 500
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aupload_file(self, public_id: str, content: bytes) -> ContextResult[UploadFileResponse]:
        return await self.__asend_request(
            HTTPMethod.POST,
            "image/upload",
            data=self.__create_request_data({"public_id": public_id}),
            files={"file": content},
            response_type=UploadFileResponse,
        )

    @as_awaitable_result
    async def aget_files(self, user_id: str, relative_folder_path: str) -> ContextResult[GetResourcesResponse]:
        return await self.__asend_request(
            HTTPMethod.GET,
            "resources/image/upload",
            query_params={"prefix": f"{user_id}/{relative_folder_path}", "max_results": self.__max_results},
            response_type=GetResourcesResponse,
        )

    @as_awaitable_result
    async def adelete_folder_recursively(self, folder_path: str) -> ContextResult[DeleteResourceResponse]:
        return await self.__asend_request(
            HTTPMethod.DELETE,
            "resources/image/upload",
            query_params={"prefix": folder_path},
            response_type=DeleteResourceResponse,
        )

    @as_awaitable_result
    async def agenerate_zip_archive(self, folder_path: str, zip_path: str) -> ContextResult[GenerateArchiveResponse]:
        return await self.__asend_request(
            HTTPMethod.POST,
            "image/generate_archive",
            data=self.__create_request_data({"prefixes": folder_path, "target_public_id": zip_path}),
            response_type=GenerateArchiveResponse,
        )

    def __create_request_data(self, params: MutableMapping[str, Any]) -> RequestData:
        # Add api_key and timestamp if not present
        if "api_key" not in params.keys():
            params["api_key"] = settings.CLOUDINARY_API_KEY
        if "timestamp" not in params.keys():
            params["timestamp"] = str(int(datetime.now(timezone.utc).timestamp()))

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

    @as_awaitable_result
    async def __asend_request[TResponse: BaseModel](
        self,
        method: HTTPMethod,
        url: str,
        *,
        query_params: Optional[QueryParamTypes] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        response_type: type[TResponse],
    ) -> ContextResult[TResponse]:
        async with self.__get_client() as client:
            response = await client.request(method, url, params=query_params, data=data, files=files)

            if response.is_error:
                self.__logger.error(f"Unexpected Cloudinary error occurred when calling {method} {response.url} {response.text}")
                return ContextResult[TResponse].failure(ErrorContext.server_error())

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
