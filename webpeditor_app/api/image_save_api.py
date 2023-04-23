import logging

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import EditedImage
from webpeditor_app.services.image_services.image_service import get_original_image, get_edited_image, \
    get_edited_image_file_path
from webpeditor_app.services.other_services.session_service import get_user_id_from_session_store, \
    update_image_editor_session
from webpeditor_app.services.validators.image_file_validator import validate_image_file_size


@requires_csrf_token
@require_http_methods(['POST'])
def image_save_api(request: WSGIRequest):
    if request.method == 'POST':
        user_id = get_user_id_from_session_store(request)

        if user_id is None:
            return redirect('ImageDoesNotExistView')

        if request.session.get_expiry_age() == 0:
            return redirect('ImageDoesNotExistView')

        original_image = get_original_image(user_id)
        if original_image is None or original_image.user_id != user_id:
            return redirect("ImageDoesNotExistView")

        edited_image = get_edited_image(user_id)
        if edited_image is None:
            return redirect("ImageDoesNotExistView")

        image_file: UploadedFile = request.FILES.get('edited_image', None)

        edited_image_path = get_edited_image_file_path(user_id, edited_image)

        if edited_image_path.exists():
            default_storage.delete(edited_image_path)
        else:
            logging.error("Path to edited image not found")

        default_storage.save(edited_image_path, image_file)

        # TODO: add popup info about image size
        try:
            validate_image_file_size(image_file)
        except ValidationError as errors:
            validation_error = "".join(str(error) for error in errors)
            return render(request, 'imageEdit.html', {'validation_error': validation_error})

        # image = open_image_with_pil(edited_image_path)
        edited_image_path_to_db = f"{user_id}/edited/{image_file.name}"

        update_image_editor_session(request=request, user_id=user_id)

        EditedImage.objects.filter(user_id=user_id).update(
            edited_image=edited_image_path_to_db,
            session_id_expiration_date=request.session.get_expiry_date()
        )

        response = HttpResponse(status=200, content_type="text/javascript")

        return response
