from http import HTTPStatus
from typing import Annotated, final

from anydi_django import container
from ninja import UploadedFile
from ninja.params.functions import File, Form
from ninja_extra import api_controller, http_get, http_post, ControllerBase  # pyright: ignore

from api.action_result import ActionResult, ActionResultWithStatus
from application.converter.commands.convert_images_command import ConvertImagesCommand
from application.converter.commands.schemas import ConversionRequest, ConversionResponse, GetZipResponse
from application.converter.queries.get_zip_query import GetZipQuery
from domain.converter.constants import ImageConverterConstants


@final
@api_controller("converter", tags="Image Converter")
class ConverterController(ControllerBase):
    @http_post(
        "convert",
        response={
            HTTPStatus.OK: ActionResult[ConversionResponse],
            HTTPStatus.NOT_FOUND: ActionResult[ConversionResponse],
            HTTPStatus.BAD_REQUEST: ActionResult[ConversionResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: ActionResult[ConversionResponse],
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
    ) -> ActionResultWithStatus[ConversionResponse]:
        async with container.arequest_context():
            convert_images_command = await container.aresolve(ConvertImagesCommand)
            conversion_request = ConversionRequest.create(files, output_format, quality)
            results = await convert_images_command.ahandle(self.context, conversion_request)
            return ActionResult[ConversionResponse].from_results(results)

    @http_get(
        "zip",
        response={
            HTTPStatus.OK: ActionResult[GetZipResponse],
            HTTPStatus.NOT_FOUND: ActionResult[GetZipResponse],
            HTTPStatus.BAD_REQUEST: ActionResult[GetZipResponse],
            HTTPStatus.INTERNAL_SERVER_ERROR: ActionResult[GetZipResponse],
        },
        summary="Get converted images as zip",
    )
    async def aget_zip(self) -> ActionResultWithStatus[GetZipResponse]:
        async with container.arequest_context():
            get_zip_query = await container.aresolve(GetZipQuery)
            result = await get_zip_query.ahandle(self.context)
            return ActionResult[GetZipResponse].from_result(result)
