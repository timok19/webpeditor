from http import HTTPStatus
from typing import Any

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import TemplateView


class ConverterView(TemplateView):
    template_name = "webpeditor_app/image-converter.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context: dict[str, Any] = self.get_context_data(**kwargs)

        context.update(
            {
                "form": "form",  # TODO: Create an empty form
                "error": request.session.get("error_message"),
                "converted_images": [],
            }
        )

        return self.render_to_response(context, status=HTTPStatus.OK)

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
