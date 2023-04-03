import io
import logging
import shutil
from decimal import Decimal

from PIL import Image
from PIL.Image import Image as ImageClass
from _decimal import ROUND_UP
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.folder_service import create_folder, get_media_root_paths
from webpeditor_app.services.other_services.session_service import update_session, get_session_id
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size
from webpeditor_app.views.image_info_view import format_image_name

logging.basicConfig(level=logging.INFO)


def get_user_id(request: WSGIRequest) -> str | None:
    try:
        user_id = request.session.get('user_id')
    except Exception as e:
        logging.error(e)
        return None
    return user_id


def get_original_image(user_id: str) -> OriginalImage | None:
    try:
        original_image = OriginalImage.objects.filter(user_id=user_id).first()
    except OriginalImage.DoesNotExist as e:
        logging.error(e)
        return None
    return original_image


def get_edited_image(user_id: str) -> EditedImage | None:
    try:
        edited_image = EditedImage.objects.filter(user_id=user_id).first()
    except EditedImage.DoesNotExist as e:
        logging.error(e)
        return None
    return edited_image


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


def copy_original_image_to_edited_folder(user_id: str,
                                         original_image: OriginalImage,
                                         edited_image: EditedImage) -> bool:
    original_image_folder_path, edited_image_folder_path = get_media_root_paths(user_id)

    storage = FileSystemStorage()

    if not edited_image_folder_path.exists():
        edited_image_folder_path = create_folder(user_id=user_id, is_original_image=False)

    original_image_file_path = original_image_folder_path / original_image.image_name
    edited_image_file_path = edited_image_folder_path / edited_image.edited_image_name

    shutil.copy2(original_image_file_path, edited_image_file_path)

    file = storage.open(
        name=f"{edited_image_folder_path}/{edited_image.edited_image_name}"
    )
    if not file:
        return False

    return True


def create_edited_image_form(edited_image: EditedImage | None):
    data = {"edited_image_file": edited_image}
    if edited_image is None:
        return EditedImageForm()
    else:
        return EditedImageForm(data=data)


def post(request: WSGIRequest, user_id: str) -> EditedImageForm:
    if request.session.get_expiry_age() == 0:
        return redirect('ImageDoesNotExistView')

    if user_id is None:
        return redirect('ImageDoesNotExistView')

    original_image = get_original_image(user_id)
    if original_image is None or original_image.user_id != user_id:
        return redirect("ImageDoesNotExistView")

    image_file: UploadedFile = request.FILES.get('edited_image_file', None)

    _, edited_image_folder_path = get_media_root_paths(user_id)
    edited_image_path = edited_image_folder_path / image_file.name

    if default_storage.exists(edited_image_path):
        default_storage.delete(edited_image_path)
    else:
        logging.error("Path not found")

    default_storage.save(edited_image_path, image_file)

    # TODO: add popup info about image size
    try:
        validate_image_file_size(image_file)
    except ValidationError as errors:
        error_str = "".join(str(error) for error in errors)
        return render(request, 'imageEdit.html', {'validation_error': error_str})

    # image = open_image_with_pil(edited_image_path)
    edited_image_path_to_db = f"{user_id}/edited/{image_file.name}"

    EditedImage.objects.filter(user_id=user_id).update(
        edited_image=edited_image_path_to_db,
        edited_image_name=image_file.name,
        content_type_edited=image_file.content_type,
        session_id_expiration_date=request.session.get_expiry_date()
    )

    update_session(request=request, user_id=user_id)


def get(request: WSGIRequest, user_id: str, session_key: str) -> EditedImageForm:
    if user_id is None:
        return redirect('ImageDoesNotExistView')

    original_image = get_original_image(user_id)
    if original_image is None or original_image.user_id != user_id:
        return redirect("ImageDoesNotExistView")

    edited_image = get_edited_image(user_id)
    if edited_image is not None and original_image.user_id != user_id:
        return redirect("ImageDoesNotExistView")

    elif edited_image is None and original_image.user_id == user_id:
        edited_image = create_and_save_edited_image(user_id, original_image, session_key, request)

        if not copy_original_image_to_edited_folder(user_id, original_image, edited_image):
            return redirect("ImageDoesNotExistView")

        edited_image_form: EditedImageForm = create_edited_image_form(edited_image)

    else:
        edited_image_form: EditedImageForm = create_edited_image_form(edited_image)

    update_session(request=request, user_id=user_id)

    return edited_image_form


def open_image_with_pil(edited_image_path: UploadedFile) -> ImageClass:
    return Image.open(edited_image_path)


def get_image_size_in_mb(image: ImageClass) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=image.format)

    size_in_bytes = buffer.tell()
    size_in_kb = size_in_bytes / 1024

    if size_in_kb >= 1024:
        # Calculate the size in megabytes
        size_in_mb = size_in_kb / 1024
        return f"{size_in_mb:.1f} MB"
    else:
        return f"{size_in_kb:.1f} KB"


def process_edited_image_form(image_form: EditedImageForm):
    image: EditedImage = image_form.data.get("edited_image_file")
    image_name = format_image_name(image.edited_image_name)
    image_file = open_image_with_pil(image.edited_image.path)
    image_size = get_image_size_in_mb(image_file)
    image_resolution = f"{image_file.width}px ⨯ {image_file.height}px"
    image_aspect_ratio: Decimal = Decimal(image_file.width / image_file.height) \
        .quantize(Decimal('.1'), rounding=ROUND_UP)
    # image_format =

    return str(image.edited_image.url), \
        image_file.format, \
        image_size, \
        image_resolution, \
        image_name, \
        image_aspect_ratio


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    user_id = get_user_id(request)
    session_key = get_session_id(request=request)
    edited_image_form: EditedImageForm = EditedImageForm()
    edited_image_format: str = ""
    edited_image_size: str = ""
    edited_image_resolution: str = ""
    edited_image_name_short_version: str = ""
    edited_image_name: str = ""
    edited_image_url_to_fe: str = ""
    edited_image_aspect_ratio: Decimal = Decimal()
    edited_image_content_type: str = ""

    if request.method == 'POST':
        response = post(request, user_id)
    else:
        response = get(request, user_id, session_key)
        edited_image = get_edited_image(user_id)
        if edited_image is not None and edited_image.content_type_edited is not None:
            edited_image_content_type = edited_image.content_type_edited
            edited_image_name = edited_image.edited_image_name

    if isinstance(response, HttpResponsePermanentRedirect) or isinstance(response, HttpResponseRedirect):
        return response

    if isinstance(response, EditedImageForm):
        edited_image_form = response

        edited_image_url_to_fe, edited_image_format, \
            edited_image_size, edited_image_resolution, \
            edited_image_name_short_version, edited_image_aspect_ratio = process_edited_image_form(edited_image_form)

    context: dict = {
        'edited_image_form': edited_image_form,
        'edited_image_url_to_fe': edited_image_url_to_fe,
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
