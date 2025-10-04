from http import HTTPStatus
from typing import Annotated, final

from anydi.ext.django import container
from ninja import UploadedFile
from ninja.params.functions import File, Form
from ninja_extra import api_controller, http_get, http_post  # pyright: ignore

from webpeditor_app.application.converter.handlers.convert_images import ConvertImages
from webpeditor_app.application.converter.handlers.get_zip import GetZip
from webpeditor_app.application.converter.handlers.schemas import ConversionRequest, ConversionResponse, GetZipResponse
from webpeditor_app.api.controllers.base import ControllerBase
from webpeditor_app.api.controllers.schemas import HTTPResult, HTTPResultWithStatus
from webpeditor_app.common.session.session_service_factory import SessionServiceFactory
from webpeditor_app.domain.converter.constants import ImageConverterConstants


@final
@api_controller("/converter", tags="Image Converter")
class ConverterController(ControllerBase):
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
            session_service_factory = await container.aresolve(SessionServiceFactory)
            convert_images = await container.aresolve(ConvertImages)
            session_service = session_service_factory.create(self.request)
            request = ConversionRequest.create(files, output_format, quality)
            results = await convert_images.ahandle(request, session_service)
            return HTTPResult[ConversionResponse].from_results(results)

    @http_get(
        "/get-zip",
        response={
            HTTPStatus.OK: HTTPResult[GetZipResponse],
            HTTPStatus.NOT_FOUND: HTTPResult[GetZipResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: HTTPResult[GetZipResponse],
        },
        summary="Get converted images as zip",
    )
    async def aget_zip(self) -> HTTPResultWithStatus[GetZipResponse]:
        async with container.arequest_context():
            session_service_factory = await container.aresolve(SessionServiceFactory)
            get_zip = await container.aresolve(GetZip)
            session_service = session_service_factory.create(self.request)
            result = await get_zip.ahandle(session_service)
            return HTTPResult[GetZipResponse].from_result(result)
