import cloudinary.uploader
from io import BytesIO
from PIL.Image import Image as ImageClass

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import EditedImage
from webpeditor_app.services.image_services.image_service import get_original_image, get_edited_image
from webpeditor_app.services.other_services.api_service import get_json_request_body
from webpeditor_app.services.other_services.session_service import get_user_id_from_session_store, update_session


@csrf_exempt
@require_http_methods(['POST'])
def image_save_api(request: WSGIRequest):
    if request.method == 'POST':
        user_id = get_user_id_from_session_store(request)
        image_file = ImageClass()
        if user_id is None:
            return redirect('NoContentView')

        if request.session.get_expiry_age() == 0:
            return redirect('ImageDoesNotExistView')

        original_image = get_original_image(user_id)
        if original_image is None or original_image.user_id != user_id:
            return redirect("ImageDoesNotExistView")

        edited_image = get_edited_image(user_id)
        if edited_image is None:
            return redirect("ImageDoesNotExistView")

        request_body = get_json_request_body(request)
        if isinstance(request_body, tuple):
            image_file: ImageClass = request_body[3]

        buffer = BytesIO()
        image_file.save(buffer, format=image_file.format)
        buffer.seek(0)

        folder_path = f"{user_id}/edited/"

        # Save image to Cloudinary
        # TODO: make sure, that this will overwrite an existing image (create if else statement)
        cloudinary_parameters: dict = {
            "folder": folder_path,
            "use_filename": True,
            "filename_override": edited_image.image_name,
            "overwrite": True
        }
        cloudinary_image = cloudinary.uploader.upload_image(file=buffer, **cloudinary_parameters)

        # Update edited image in DB
        EditedImage.objects.filter(user_id=user_id).update(
            image_url=cloudinary_image.url,
            session_id_expiration_date=request.session.get_expiry_date(),
        )

        update_session(request=request, user_id=user_id)

        response = HttpResponse(status=200, content_type="text/javascript")

        return response
