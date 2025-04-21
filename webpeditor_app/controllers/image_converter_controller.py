from http import HTTPStatus
from typing import Annotated, final

from anydi.ext.django import container
from ninja import UploadedFile
from ninja.params.functions import File, Form
from ninja_extra import ControllerBase, api_controller, http_post  # pyright: ignore [reportUnknownVariableType]

from webpeditor_app.application import ConvertImages, SessionServiceFactory
from webpeditor_app.application.converter.schemas.conversion import ConversionRequest, ConversionResponse
from webpeditor_app.application.converter.schemas.download import DownloadAllZipResponse
from webpeditor_app.application.converter.schemas.output_formats import ImageConverterAllOutputFormats
from webpeditor_app.controllers.mixins.controller_mixin import ControllerMixin
from webpeditor_app.controllers.schemas.http_result import HTTPResult, HTTPResultListWithStatus, HTTPResultWithStatus


# TODO: Add other endpoints from "__converter" folder


@final
@api_controller("/converter", tags="Image Converter")
class ImageConverterController(ControllerMixin, ControllerBase):
    @http_post(
        "/convert-images",
        response={
            HTTPStatus.OK: list[HTTPResult[ConversionResponse]],
            HTTPStatus.BAD_REQUEST: list[HTTPResult[ConversionResponse]],
            HTTPStatus.INTERNAL_SERVER_ERROR: list[HTTPResult[ConversionResponse]],
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
    ) -> HTTPResultListWithStatus[ConversionResponse]:
        async with container.arequest_context():
            session_service_factory = await container.aresolve(SessionServiceFactory)
            session_service = session_service_factory.create(self.get_request(self.context))
            convert_images = await container.aresolve(ConvertImages)
            request = ConversionRequest.create(files, output_format, quality)
            results = await convert_images.handle_async(request, session_service)
            return HTTPResult[ConversionResponse].from_results(results)

    @http_post(
        "/download-all-zip",
        response={
            HTTPStatus.OK: HTTPResult[DownloadAllZipResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: HTTPResult[DownloadAllZipResponse],
        },
    )
    async def download_all_as_zip_async(self) -> HTTPResultWithStatus[DownloadAllZipResponse]:
        # session_service = self.__session_service_factory.create(self.get_request(self.context))
        return HTTPResult[DownloadAllZipResponse].failure_500("Not implemented")
