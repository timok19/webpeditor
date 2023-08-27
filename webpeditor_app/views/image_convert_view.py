import logging

from django.core.handlers.asgi import ASGIRequest
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.forms.forms import ImagesToConvertForm
from webpeditor_app.commands.converted_images_commands import ConvertedImagesCommands

from webpeditor_app.services.other_services.session_service import SessionService

logging.basicConfig(level=logging.INFO)


@requires_csrf_token
@require_http_methods(["GET"])
def image_convert_view(request: ASGIRequest):
    session_service = SessionService(request)
    user_id = session_service.user_id

    converted_images_commands = ConvertedImagesCommands(user_id)

    image_form = ImagesToConvertForm()

    context = {
        "form": image_form,
        "error": request.session.get("error_message"),
        "converted_images": request.session.get("converted_images")
        if converted_images_commands.get_converted_image()
        else None,
    }
    return render(request, "imageConvert.html", context, status=200)
