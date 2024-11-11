from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from webpeditor_app.models import OriginalImageAsset


def get_user_id_or_401(request: WSGIRequest) -> str | HttpResponse:
    user_id: str | None = get_unsigned_user_id(request)

    if user_id is None:
        return render(request, "webpeditor_app/imageIsNotUploadedView.html", status=401)

    return user_id


def get_original_image_or_401(request: WSGIRequest, user_id: str) -> OriginalImageAsset | HttpResponse:
    original_image: OriginalImageAsset | None = get_original_image(user_id)

    if original_image is None or original_image.user_id != user_id:
        return render(request, "webpeditor_app/imageIsNotUploadedView.html", status=401)

    return original_image
