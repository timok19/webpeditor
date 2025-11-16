from http import HTTPStatus
from typing import Any, override

from asgiref.sync import sync_to_async
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import FormView
from httpx import AsyncClient

from views.forms import ImageConverterUploadFilesForm


class ImageConverterView(FormView[ImageConverterUploadFilesForm]):
    template_name = "webpeditor_app/image-converter.html"
    form_class = ImageConverterUploadFilesForm

    @override
    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore
        context: dict[str, Any] = self.get_context_data(**kwargs)

        # Use sync_to_async to access session data
        error_message = await sync_to_async(lambda: request.session.get("error_message"))()

        context.update(
            {
                "form": "form",  # TODO: Create an empty form
                "error": error_message,
                "converted_images": [],
            }
        )
        return await sync_to_async(self.render_to_response)(context, status=HTTPStatus.OK)

    @override
    async def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore
        # Use sync_to_async for any potential session operations
        absolute_uri = await sync_to_async(lambda: request.build_absolute_uri("/api/converter/convert-images"))()

        # TODO
        async with AsyncClient() as client:
            await client.post(absolute_uri)

        return HttpResponse()

    @override
    async def put(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # pyright: ignore
        return await self.post(request, *args, **kwargs)

    # image_form: ImageConverterForm = ImageConverterForm()
    # user_id: str | None = get_unsigned_user_id(request)
    #
    # if user_id is None:
    #     return render(request, "webpeditor_app/image-not-uploaded.html", context={"form": image_form}, status=401)
    #
    # return render(
    #     request,
    #     "webpeditor_app/image-converter.html",
    #     context={
    #         "form": image_form,
    #         "error": request.session.get("error_message"),
    #         "converted_images": request.session.get("converted_images") if get_converted_image(user_id) else None,
    #     },
    #     status=200,
    # )
