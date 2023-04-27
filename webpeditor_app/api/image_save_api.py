import cloudinary.uploader
import cloudinary.api
from io import BytesIO
from PIL.Image import Image as ImageClass

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import EditedImage
from webpeditor_app.services.image_services.image_service import get_original_image, get_edited_image
from webpeditor_app.services.api_services.request_service import get_json_request_body
from webpeditor_app.services.other_services.session_service import get_unsigned_user_id, update_session


@csrf_exempt
@require_http_methods(['POST'])
def image_save_api(request: WSGIRequest):
    if request.method == 'POST':
        image_file = ImageClass()
        
        user_id = get_unsigned_user_id(request)
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

        resources = cloudinary.api.resources(
            prefix=f"{user_id}/edited",
            type="upload"
        )

        public_ids: list = [resource["public_id"] for resource in resources["resources"]]

        # Save image to Cloudinary
        cloudinary_parameters: dict = {
            "public_id": public_ids[0],
            "overwrite": True
        }
        cloudinary_image = cloudinary.uploader.upload_image(file=buffer, **cloudinary_parameters)

        update_session(request=request, user_id=user_id)
        # Update edited image in DB
        EditedImage.objects.filter(user_id=user_id).update(image_url=cloudinary_image.url)

        return HttpResponse(status=200, content_type="text/javascript")
