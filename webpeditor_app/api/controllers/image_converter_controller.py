from http import HTTPStatus
from typing import Annotated, final

from anydi.ext.django import container
from ninja import UploadedFile
from ninja.params.functions import File, Form
from ninja_extra import api_controller, http_post  # pyright: ignore

from webpeditor_app.application.common.session_service import SessionServiceFactory
from webpeditor_app.application.converter.handlers.convert_images_handler import ConvertImagesHandler
from webpeditor_app.application.converter.handlers.schemas import (
    ConversionRequest,
    ConversionResponse,
    DownloadAllZipResponse,
    ImageConverterAllOutputFormats,
)
from webpeditor_app.api.controllers.base import ControllerBase
from webpeditor_app.api.controllers.schemas import HTTPResult, HTTPResultWithStatus


@final
@api_controller("/converter", tags="Image Converter")
class ImageConverterController(ControllerBase):
    @http_post(
        "/convert-images",
        response={
            HTTPStatus.OK: HTTPResult[ConversionResponse],
            HTTPStatus.BAD_REQUEST: HTTPResult[ConversionResponse],
            HTTPStatus.NOT_FOUND: HTTPResult[ConversionResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: HTTPResult[ConversionResponse],
        },
        summary="Convert images",
    )
    async def aconvert_images(
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
    ) -> HTTPResultWithStatus[ConversionResponse]:
        async with container.arequest_context():
            session_service_factory = await container.aresolve(SessionServiceFactory)
            convert_images_handler = await container.aresolve(ConvertImagesHandler)
            session_service = session_service_factory.create(self.request)
            request = ConversionRequest.create(files, output_format, quality)
            results = await convert_images_handler.ahandle(request, session_service)
            return HTTPResult[ConversionResponse].from_results(results)

    @http_post(
        "/download-all-zip",
        response={
            HTTPStatus.OK: HTTPResult[DownloadAllZipResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: HTTPResult[DownloadAllZipResponse],
        },
        summary="Download all zip files",
    )
    async def adownload_all_as_zip(self) -> HTTPResultWithStatus[DownloadAllZipResponse]:
        # session_service = self.__session_service_factory.create(self.get_request(self.context))
        return HTTPResult[DownloadAllZipResponse].failure_500("Not implemented")
