from http import HTTPStatus
from typing import Annotated, final, Final

from ninja import UploadedFile
from ninja.params.functions import File, Form
from ninja_extra import ControllerBase, api_controller, http_post

from webpeditor_app.application.converter.commands.convert_images import ConvertImages
from webpeditor_app.application.converter.schemas.conversion import ConversionResponse, ConversionRequest
from webpeditor_app.application.converter.schemas.download import DownloadAllZipResponse
from webpeditor_app.application.converter.schemas.settings import ImageConverterAllOutputFormats
from webpeditor_app.controllers.mixins.controller_mixin import ControllerMixin
from webpeditor_app.controllers.schemas.result_response import ResultResponse
from webpeditor_app.application.auth.session_service_factory import SessionServiceFactory

# TODO: Add other endpoints from "__converter" folder


@final
@api_controller("/converter", tags=["Image Converter"])  # pyright: ignore [reportArgumentType]
class ImageConverterController(ControllerMixin, ControllerBase):
    def __init__(self) -> None:
        from webpeditor_app.core.di_container import DiContainer

        self.__session_service_factory: Final[SessionServiceFactory] = DiContainer.get_dependency(SessionServiceFactory)
        self.__convert_images: Final[ConvertImages] = DiContainer.get_dependency(ConvertImages)

    @http_post(
        "/convert-images",
        response={
            HTTPStatus.OK: list[ResultResponse[ConversionResponse]],
            HTTPStatus.BAD_REQUEST: list[ResultResponse[ConversionResponse]],
            HTTPStatus.INTERNAL_SERVER_ERROR: list[ResultResponse[ConversionResponse]],
        },
    )
    async def convert_images_async(
        self,
        output_format: Annotated[
            ImageConverterAllOutputFormats,
            Form(
                default=ImageConverterAllOutputFormats.WEBP,
                title="Output format",
                description="Choose image file format to convert",
            ),
        ],
        quality: Annotated[
            int,
            Form(
                ge=5,
                le=100,
                example=50,
                title="Quality",
                description="Set quality of output image. Must be >= 5 and <= 100",
            ),
        ],
        files: Annotated[
            list[UploadedFile],
            File(
                title="Files",
                description="Upload files to be converted into different format",
            ),
        ],
    ) -> tuple[HTTPStatus, list[ResultResponse[ConversionResponse]]]:
        session_service = self.__session_service_factory.create(self.get_request(self.context))
        return ResultResponse[ConversionResponse].from_multiple_results(
            await self.__convert_images.handle_async(
                request=ConversionRequest(
                    files=files,
                    options=ConversionRequest.Options(
                        output_format=output_format,
                        quality=quality,
                    ),
                ),
                session_service=session_service,
            )
        )

    @http_post(
        "/download-all-zip",
        response={
            HTTPStatus.OK: ResultResponse[DownloadAllZipResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: ResultResponse[DownloadAllZipResponse],
        },
        exclude_none=True,
    )
    async def download_all_as_zip_async(self) -> tuple[HTTPStatus, ResultResponse[DownloadAllZipResponse]]:
        session_service = self.__session_service_factory.create(self.get_request(self.context))
        return ResultResponse[DownloadAllZipResponse].failure_500("Not implemented")
