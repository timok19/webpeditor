from types import NoneType

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def image_delete_converted_api(request: WSGIRequest) -> JsonResponse:
    if request.method == "POST":
        user_id: str | None = get_unsigned_user_id(request)
        if isinstance(user_id, NoneType):
            return ResultJsonResponse(result=Result.ERROR, message="User Id was not found", status_code=401)

        request_body: JsonResponse | str = extract_image_name_from_request_body(request)
        if isinstance(request_body, JsonResponse):
            return request_body

        converted_image: ConverterImageAsset | None = get_converted_image(user_id)
        if isinstance(converted_image, NoneType):
            return ResultJsonResponse(result=Result.ERROR, message="Converted image was not found in db", status_code=404)

        public_id: str = request_body

        image_set_list: list = converted_image.image_data
        # Delete image in cloudinary
        delete_assets_in_specific_user_folder(user_id, public_id)

        filtered_image_set_list = [image_set for image_set in image_set_list if image_set["public_id"] != public_id]
        converted_image.image_data = filtered_image_set_list
        converted_image.save()

        converted_images: list[tuple] | None = request.session.get("converted_image")
        if converted_images is None:
            return ResultJsonResponse(result=Result.ERROR, message="Converted images not found", status_code=404)

        request.session["converted_images"] = [image for image in converted_images if public_id not in image]

        update_session(request=request, user_id=user_id)

        return ResultJsonResponse(result=Result.SUCCESS, message="Image has been deleted successfully", status_code=200)
    else:
        return ResultJsonResponse(result=Result.ERROR, message="Forbidden request", status_code=405)
