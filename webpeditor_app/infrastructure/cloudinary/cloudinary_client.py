from http import HTTPMethod
from typing import Final, final
from httpx import AsyncClient, BasicAuth, QueryParams
from pydantic import BaseModel

from webpeditor import settings
from webpeditor_app.infrastructure.cloudinary.schemas.resource import GetResourcesResponse
from webpeditor_app.infrastructure.cloudinary.schemas.request_builder import RequestBuilder


@final
class CloudinaryClient:
    def __init__(self) -> None:
        self.__max_results: Final[int] = 500

    async def get_resources(self, user_id: str) -> GetResourcesResponse:
        builder = RequestBuilder[None](HTTPMethod.GET, "/resources/image/upload")
        params = QueryParams({"prefix": user_id, "max_results": self.__max_results})
        return await self.__send_request(builder.with_params(params), GetResourcesResponse)

    async def __send_request[TRequest: (BaseModel, None), TResponse: BaseModel](
        self,
        request_builder: RequestBuilder[TRequest],
        response_type: type[TResponse],
    ) -> TResponse:
        request = request_builder.build()
        async with self.__get_client() as client:
            response = await client.request(
                request.method,
                request.url,
                content=request.content,
                params=request.params,
                json=request.data.model_dump() if request.data is not None else None,
            )

        response.raise_for_status()

        return response_type.model_validate_json(response.content)

    @staticmethod
    def __get_client() -> AsyncClient:
        return AsyncClient(
            base_url=f"{settings.CLOUDINARY_BASE_URL}/v1_1/{settings.CLOUDINARY_CLOUD_NAME}",
            auth=BasicAuth(
                username=settings.CLOUDINARY_API_KEY,
                password=settings.CLOUDINARY_API_SECRET,
            ),
        )
