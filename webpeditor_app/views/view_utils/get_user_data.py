from types import NoneType
from uuid import UUID

from django.core.handlers.asgi import ASGIRequest
from django.shortcuts import render
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_protect

from webpeditor_app.database.models.original_image_model import OriginalImage
from webpeditor_app.commands.original_images_commands import OriginalImagesCommands

from webpeditor_app.services.other_services.session_service import SessionService


def get_user_id_or_401(request: ASGIRequest):
    session_service = SessionService(request)
    user_id: UUID = session_service.user_id

    if isinstance(user_id, NoneType):
        return render(
            request=request,
            template_name="imageIsNotUploadedView.html",
            status=401,
        )

    return user_id


async def get_original_image_or_401(
    request: ASGIRequest,
    user_id: UUID,
):
    original_images_commands = OriginalImagesCommands(user_id)

    original_image: OriginalImage | None = (
        await original_images_commands.get_original_image()
    )
    if isinstance(original_image, NoneType) or original_image.image.user_id != user_id:
        return render(request, "imageIsNotUploadedView.html", status=401)

    return original_image


def async_csrf_protect(view_func):
    @sync_to_async
    def _wrapped_view(request, *args, **kwargs):
        # This will run the view function in a synchronous context
        sync_view = csrf_protect(view_func)
        return sync_view(request, *args, **kwargs)

    return _wrapped_view
