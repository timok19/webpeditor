from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_service import get_original_image
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id


def get_user_id_or_401(request: WSGIRequest) -> str | HttpResponse:
    user_id: str | None = get_unsigned_user_id(request)
    if isinstance(user_id, NoneType):
        return render(request, "imageIsNotUploadedView.html", status=401)

    return user_id


def get_original_image_or_401(request: WSGIRequest, user_id: str) -> OriginalImage | HttpResponse:
    original_image: OriginalImage | None = get_original_image(user_id)
    if isinstance(original_image, NoneType) or original_image.user_id != user_id:
        return render(request, "imageIsNotUploadedView.html", status=401)

    return original_image
