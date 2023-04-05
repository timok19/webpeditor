import logging

from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_service import \
    get_image_file_size, \
    get_original_image, \
    get_edited_image, \
    copy_original_image_to_edited_folder, \
    get_edited_image_file_path, \
    get_image_file_instance, \
    get_image_aspect_ratio
from webpeditor_app.services.other_services.session_service import update_session, get_session_id, get_user_id
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size
from webpeditor_app.views.image_info_view import format_image_file_name

logging.basicConfig(level=logging.INFO)


def create_and_save_edited_image(user_id: str,
                                 original_image: OriginalImage,
                                 session_key: str,
                                 request: WSGIRequest) -> EditedImage:
    new_edited_image_name = f"webpeditor_1_{original_image.image_name}"

    edited_image = f"{user_id}/edited/{new_edited_image_name}"

    edited_image_init = EditedImage(
        user_id=user_id,
        edited_image=edited_image,
        edited_image_name=new_edited_image_name,
        content_type_edited=original_image.content_type,
        session_id=session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        original_image=original_image
    )
    edited_image_init.save()

    return edited_image_init


def create_edited_image_form(edited_image: EditedImage | None) -> EditedImageForm:
    data = {"edited_image": edited_image}
    if edited_image is None:
        return EditedImageForm()
    else:
        return EditedImageForm(data=data)


def process_edited_image_form(image_form: EditedImageForm):
    image: EditedImage = image_form.data.get("edited_image")
    image_name = format_image_file_name(image.edited_image_name)
    image_file = get_image_file_instance(image.edited_image.path)
    image_size = get_image_file_size(image_file)
    image_resolution = f"{image_file.width}px ⨯ {image_file.height}px"
    image_aspect_ratio = get_image_aspect_ratio(image_file)

    # TODO: make sure, that on FE will be shown image with original format

    return str(image.edited_image.url), \
        image_file.format, \
        image_size, \
        image_resolution, \
        image_name, \
        image_aspect_ratio


def post(request: WSGIRequest, user_id: str) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    if request.session.get_expiry_age() == 0:
        return redirect('ImageDoesNotExistView')

    if user_id is None:
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

    EditedImage.objects.filter(user_id=user_id).update(
        edited_image=edited_image_path_to_db,
        edited_image_name=image_file.name,
        content_type_edited=image_file.content_type,
        session_id_expiration_date=request.session.get_expiry_date()
    )

    update_session(request=request, user_id=user_id)


def get(request: WSGIRequest,
        user_id: str,
        session_key: str) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    if user_id is None:
        return redirect('ImageDoesNotExistView')

    original_image = get_original_image(user_id)
    if original_image is None:
        return redirect("ImageDoesNotExistView")

    if original_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")

    edited_image = get_edited_image(user_id)
    if edited_image and original_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")

    elif edited_image is None and original_image.user_id == user_id:
        edited_image = create_and_save_edited_image(user_id, original_image, session_key, request)

        if not copy_original_image_to_edited_folder(user_id, original_image, edited_image):
            return redirect("ImageDoesNotExistView")

        edited_image_form: EditedImageForm = create_edited_image_form(edited_image)

    else:
        edited_image_form: EditedImageForm = create_edited_image_form(edited_image)

    update_session(request=request, user_id=user_id)

    edited_image_url, \
        edited_image_format, \
        edited_image_size, \
        edited_image_resolution, \
        edited_image_name_short_version, \
        edited_image_aspect_ratio = process_edited_image_form(edited_image_form)

    edited_image = get_edited_image(user_id)
    edited_image_content_type = edited_image.content_type_edited
    edited_image_name = edited_image.edited_image_name

    context: dict = {
        'image_form': edited_image_form,
        'edited_image_url': edited_image_url,
        'edited_image_format': edited_image_format,
        'edited_image_size': edited_image_size,
        'edited_image_resolution': edited_image_resolution,
        'edited_image_name_short_version': edited_image_name_short_version,
        'edited_image_name': edited_image_name,
        'edited_image_aspect_ratio': edited_image_aspect_ratio,
        'csrf_token_value': get_token(request),
        'edited_image_content_type': edited_image_content_type
    }

    return render(request, 'imageEdit.html', context)


@requires_csrf_token
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    user_id = get_user_id(request)
    session_key = get_session_id(request)

    if request.method == 'POST':
        response = post(request, user_id)
        return response

    elif request.method == "GET":
        response = get(request, user_id, session_key)
        return response

    else:
        return HttpResponse(status=405)
