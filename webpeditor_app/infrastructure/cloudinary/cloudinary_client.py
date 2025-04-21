from dataclasses import dataclass
from http import HTTPMethod
from typing import Final, final
from httpx import AsyncClient, BasicAuth, QueryParams
from ninja import Schema

from webpeditor.settings import CLOUDINARY_BASE_URL, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
from webpeditor_app.infrastructure.cloudinary.schemas.resource import GetResourcesResponse
from webpeditor_app.infrastructure.cloudinary.schemas.request_builder import Request, RequestBuilder


@final
@dataclass
class CloudinaryClient:
    def __init__(self) -> None:
        self.__max_results: Final[int] = 500

    async def get_resources(self, user_id: str) -> GetResourcesResponse:
        return await self.__send_request(
            RequestBuilder(HTTPMethod.GET, "/resources/image/upload")
            .with_params(QueryParams(**{"prefix": user_id, "max_results": self.__max_results}))
            .build(),
            GetResourcesResponse,
        )

    async def __send_request[TRequest: Schema, TResponse: Schema](
        self,
        request: Request[TRequest],
        response_type: type[TResponse],
    ) -> TResponse:
        async with self.__get_client() as client:
            response = await client.request(
                request.method,
                request.url,
                content=request.content,
                params=request.params,
                data=request.data.model_dump() if request.data is not None else None,
            )

        response.raise_for_status()

        return response_type.model_validate_json(response.content)

    @staticmethod
    def __get_client() -> AsyncClient:
        return AsyncClient(
            base_url=f"{CLOUDINARY_BASE_URL}/v1_1/{CLOUDINARY_CLOUD_NAME}",
            auth=BasicAuth(
                username=CLOUDINARY_API_KEY,
                password=CLOUDINARY_API_SECRET,
            ),
        )
