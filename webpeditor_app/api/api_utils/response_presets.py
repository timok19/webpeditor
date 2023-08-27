from types import NoneType
from typing import Tuple

from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponseRedirect, JsonResponse

from webpeditor_app.services.other_services.session_service import SessionService


def unauthorized_access_response() -> HttpResponseRedirect:
    response = HttpResponseRedirect(redirect_to="/unauthorized_access/")
    response.content = "Unauthorized access"
    response.status_code = 401

    return response


def get_user_id_and_converted_images(
    request: ASGIRequest,
) -> JsonResponse | Tuple[str, list]:
    session_service = SessionService(request)
    user_id = session_service.user_id

    if isinstance(user_id, NoneType):
        return JsonResponse({"error": "User Id was not found"}, status=401)

    converted_images: list | None = request.session.get("converted_images")
    if isinstance(converted_images, NoneType):
        return JsonResponse({"error": "Converted images not found"}, status=404)

    return user_id, converted_images
