from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods


@requires_csrf_token
@require_http_methods(["GET"])
def image_convert_view(request: WSGIRequest) -> HttpResponse:
    image_form: ImageConverterForm = ImageConverterForm()
    user_id: str | None = get_unsigned_user_id(request)

    if user_id is None:
        return render(request, "webpeditor_app/imageIsNotUploadedView.html", context={"form": image_form}, status=401)

    return render(
        request,
        "webpeditor_app/imageConvert.html",
        context={
            "form": image_form,
            "error": request.session.get("error_message"),
            "converted_images": request.session.get("converted_images") if get_converted_image(user_id) else None,
        },
        status=200,
    )
