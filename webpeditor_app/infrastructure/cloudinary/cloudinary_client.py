import hashlib
from datetime import datetime, timezone
from http import HTTPMethod
from typing import Final, MutableMapping, Optional, final, Collection

from httpx import AsyncClient, BasicAuth, Timeout
from pydantic import BaseModel

from webpeditor import settings
from webpeditor_app.core.abc.logger_abc import LoggerABC
from webpeditor_app.core.result import ContextResult, ErrorContext, as_awaitable_result
from webpeditor_app.core.utils import BoolUtils
from webpeditor_app.infrastructure.cloudinary.schemas import (
    DeleteFileResponse,
    GetFilesResponse,
    UploadFileResponse,
)
from webpeditor_app.infrastructure.cloudinary.schemas.zip import GenerateZipResponse
from webpeditor_app.infrastructure.cloudinary.types import QueryParamTypes, RequestData, RequestFiles


@final
class CloudinaryClient:
    __MAX_RESULTS: Final[int] = 500
    __EXPIRATION_IN_SECONDS: Final[int] = 60 * 15  # 15 minutes

    def __init__(self, logger: LoggerABC) -> None:
        self.__logger: Final[LoggerABC] = logger

    @as_awaitable_result
    async def aupload_file(
        self,
        folder: str,
        public_id: str,
        content: bytes,
    ) -> ContextResult[UploadFileResponse]:
        return await self.__asend_request(
            HTTPMethod.POST,
            "image/upload",
            data=self.__create_request_data_with_signature(
                {
                    "public_id": public_id,
                    "asset_folder": folder,
                    "use_filename": BoolUtils.to_str(True),
                    "overwrite": BoolUtils.to_str(True),
                    "access_mode": "public",
                }
            ),
            files={"file": content},
            response_type=UploadFileResponse,
        )

    @as_awaitable_result
    async def aget_files(self, folder_path: str) -> ContextResult[GetFilesResponse]:
        return await self.__asend_request(
            HTTPMethod.GET,
            "resources/by_asset_folder",
            query_params={"asset_folder": folder_path, "max_results": self.__MAX_RESULTS},
            response_type=GetFilesResponse,
        )

    @as_awaitable_result
    async def adelete_files(self, public_ids: Collection[str]) -> ContextResult[DeleteFileResponse]:
        return await self.__asend_request(
            HTTPMethod.DELETE,
            "resources/image/upload",
            query_params="&".join(f"public_ids[]={public_id}" for public_id in public_ids),
            response_type=DeleteFileResponse,
        )

    @as_awaitable_result
    async def agenerate_zip_archive(self, public_ids: Collection[str], zip_file_path: str) -> ContextResult[GenerateZipResponse]:
        expires_at = str(int(datetime.now(timezone.utc).timestamp()) + self.__EXPIRATION_IN_SECONDS)
        params = {
            "resource_type": "image",
            "type": "upload",
            "target_format": "zip",
            "public_ids": ",".join(public_ids),
            "target_public_id": zip_file_path,
            "mode": "create",
            "expires_at": expires_at,
        }
        request_data = self.__create_request_data_with_signature(params)
        request_data.pop("public_ids")
        request_data.setdefault("public_ids[]", list(public_ids))

        return await self.__asend_request(
            HTTPMethod.POST,
            "image/generate_archive",
            data=request_data,
            files=[],  # Force multipart/form-data
            response_type=GenerateZipResponse,
        )

    def __create_request_data_with_signature(self, params: MutableMapping[str, str]) -> RequestData:
        keys = params.keys()
        if "api_key" not in keys:
            params["api_key"] = settings.CLOUDINARY_API_KEY
        if "timestamp" not in keys:
            params["timestamp"] = str(int(datetime.now(timezone.utc).timestamp()))
        if "signature" not in keys:
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
    async def __asend_request[T: BaseModel](
        self,
        method: HTTPMethod,
        url: str,
        *,
        query_params: Optional[QueryParamTypes] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        response_type: type[T],
    ) -> ContextResult[T]:
        async with self.__get_client() as client:
            response = await client.request(method, url, params=query_params, data=data, files=files)
            if response.is_error:
                self.__logger.error(f"Unexpected Cloudinary error occurred: {method} {response.status_code} {response.url} {response.text}")
                return ContextResult[T].failure(ErrorContext.bad_request("Invalid request"))

            return ContextResult[T].success(response_type.model_validate(response.json()))

    @staticmethod
    def __get_client() -> AsyncClient:
        return AsyncClient(
            base_url=f"{settings.CLOUDINARY_BASE_URL}/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/",
            auth=BasicAuth(
                username=settings.CLOUDINARY_API_KEY,
                password=settings.CLOUDINARY_API_SECRET,
            ),
            timeout=Timeout(
                connect=10.0,
                read=float(settings.CLOUDINARY_HTTP_TIMEOUT_SECONDS),
                write=30.0,
                pool=5.0,
            ),
        )
