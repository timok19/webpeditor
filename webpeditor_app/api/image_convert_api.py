from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import requires_csrf_token, csrf_protect
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from webpeditor_app.forms.forms import ImagesToConvertForm
from webpeditor_app.services.image_services.image_converter_service import (
    ImageConverterService,
)
from webpeditor_app.services.image_services.types import AllowedImageFormats
from webpeditor_app.services.other_services.session_service import SessionService

from webpeditor_app.services.validators.image_file_validator import validate_images


@requires_csrf_token
@csrf_protect
@require_http_methods(["POST"])
async def image_convert_api(request: ASGIRequest):
    session_service = SessionService(request)

    if request.method == "POST":
        user_id = session_service.user_id
        if user_id is None:
            session_service.add_new_signed_user_id_to_session_store()
            user_id = session_service.get_unsigned_user_id()

        session_service.set_session_expiry(900)

        image_form = ImagesToConvertForm(request.POST, request.FILES)
        if not image_form.is_valid():
            request.session["error_message"] = "One or many file(s) has unknown format"
            request.session["converted_images"] = None
            return HttpResponseRedirect(reverse("ImageConvertView"), status=400)

        image_files = request.FILES.getlist("images_to_convert")

        # Validate image size
        if (
            isinstance(image_files, list)
            and validate_images(request, image_files) is False
        ):
            return HttpResponseRedirect(reverse("ImageConvertView"), status=500)

        output_format: str = request.POST.get("output_format")
        quality: str = request.POST.get("quality")

        try:
            image_converter_service = ImageConverterService(
                user_id=user_id,
                request=request,
                image_files=image_files,
                quality=int(quality),
                output_format=AllowedImageFormats.from_str(output_format),
            )

            converted_images = await image_converter_service.run_conversion_task()
            await session_service.update_session()

            request.session.pop("error_message", None)
            request.session.pop("converted_images", None)
            request.session["converted_images"] = converted_images

            return HttpResponseRedirect(reverse("ImageConvertView"))

        except Exception as e:
            response = HttpResponse()
            response.content = str(e)
            response.status_code = 500

            return response
