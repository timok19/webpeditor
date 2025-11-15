from http import HTTPStatus
from typing import Annotated, final

from anydi_django import container
from ninja import UploadedFile
from ninja.params.functions import File, Form
from ninja_extra import api_controller, http_get, http_post  # pyright: ignore

from webpeditor_app.application.converter.commands.convert_images_command import ConvertImagesCommand
from webpeditor_app.application.converter.queries.get_zip_query import GetZipQuery
from webpeditor_app.application.converter.commands.schemas import ConversionRequest, ConversionResponse, GetZipResponse
from webpeditor_app.api.controllers.base import ControllerBase
from webpeditor_app.api.controllers.schemas import HTTPResult, HTTPResultWithStatus
from webpeditor_app.domain.converter.constants import ImageConverterConstants


@final
@api_controller("/converter", tags="Image Converter")
class ConverterController(ControllerBase):
    @http_post(
        "/convert",
        response={
            HTTPStatus.OK: HTTPResult[ConversionResponse],
            HTTPStatus.NOT_FOUND: HTTPResult[ConversionResponse],
            HTTPStatus.BAD_REQUEST: HTTPResult[ConversionResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: HTTPResult[ConversionResponse],
        },
        summary="Convert images",
    )
    async def aconvert_images(
        self,
        output_format: Annotated[
            ConversionRequest.Options.OutputFormats,
            Form(
                default=ConversionRequest.Options.OutputFormats.WEBP,
                title="Output format",
                description="Choose image file format to convert",
            ),
        ],
        quality: Annotated[
            int,
            Form(
                ge=ImageConverterConstants.MIN_QUALITY,
                le=ImageConverterConstants.MAX_QUALITY,
                example=50,
                title="Quality",
                description=f"Set quality of output image. Must be >= {ImageConverterConstants.MIN_QUALITY} and <= {ImageConverterConstants.MAX_QUALITY}",
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
            convert_images = await container.aresolve(ConvertImagesCommand)
            request = ConversionRequest.create(files, output_format, quality)
            results = await convert_images.ahandle(self.request, request)
            return HTTPResult[ConversionResponse].from_results(results)

    @http_get(
        "/zip",
        response={
            HTTPStatus.OK: HTTPResult[GetZipResponse],
            HTTPStatus.NOT_FOUND: HTTPResult[GetZipResponse],
            HTTPStatus.BAD_REQUEST: HTTPResult[GetZipResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: HTTPResult[GetZipResponse],
        },
        summary="Get converted images as zip",
    )
    async def aget_zip(self) -> HTTPResultWithStatus[GetZipResponse]:
        async with container.arequest_context():
            get_zip = await container.aresolve(GetZipQuery)
            result = await get_zip.ahandle(self.request)
            return HTTPResult[GetZipResponse].from_result(result)
