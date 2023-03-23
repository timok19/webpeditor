import io
import shutil
from decimal import Decimal

from PIL import Image
from PIL.Image import Image as ImageClass
from _decimal import ROUND_UP
from django.core.files.storage import FileSystemStorage
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.user_folder_service import create_new_folder, get_media_root_paths
from webpeditor_app.services.other_services.session_service import update_session, get_session_id
from webpeditor_app.views.image_info_view import format_image_name


def get_user_id(request: WSGIRequest) -> str | None:
    try:
        user_id = request.session['user_id']
    except Exception as e:
        print(e)
        return None
    return user_id


def get_original_image(user_id: str) -> OriginalImage | None:
    try:
        original_image = OriginalImage.objects.filter(user_id=user_id).first()
    except OriginalImage.DoesNotExist as e:
        print(e)
        return None
    return original_image


def get_edited_image(user_id: str) -> EditedImage | None:
    try:
        edited_image = EditedImage.objects.filter(user_id=user_id).first()
    except EditedImage.DoesNotExist as e:
        print(e)
        return None
    return edited_image


def create_and_save_edited_image(user_id: str,
                                 original_image: OriginalImage,
                                 session_key: str,
                                 request: WSGIRequest) -> EditedImage:
    new_edited_image_name = f"webpeditor_1_{original_image.image_name}"
    edited_image_url = f"{user_id}/edited/{new_edited_image_name}"
    edited_image_init = EditedImage(
        user_id=user_id,
        edited_image_url=edited_image_url,
        edited_image_name=new_edited_image_name,
        content_type_edited=original_image.content_type,
        session_id=session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        original_image_file=original_image
    )
    edited_image_init.save()
    return edited_image_init


def copy_original_image_to_edited_folder(user_id: str,
                                         original_image: OriginalImage,
                                         edited_image: EditedImage) -> bool:

    original_image_folder_path, edited_image_folder_path = get_media_root_paths(user_id)
    storage = FileSystemStorage()

    if not edited_image_folder_path.exists():
        edited_image_folder_path = create_new_folder(user_id=user_id, uploaded_image_folder_status=False)

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
    data = {"edited_image_url": edited_image.edited_image_url}
    if edited_image is None:
        return EditedImageForm()
    else:
        return EditedImageForm(data=data)


def handle_post_request(request: WSGIRequest, user_id: str):
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

    edited_image_form = create_edited_image_form(edited_image)
    if edited_image_form.is_valid():
        update_session(request=request, user_id=user_id)
        return edited_image_form


def handle_get_request(request: WSGIRequest, user_id: str, session_key: str):
    if user_id is None:
        return redirect('ImageDoesNotExistView')

    original_image = get_original_image(user_id)
    if original_image is None or original_image.user_id != user_id:
        return redirect("ImageDoesNotExistView")

    edited_image = get_edited_image(user_id)
    if (edited_image is None or edited_image is not None) and original_image.user_id != user_id:
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


def open_image_with_pil(edited_image_url: ImageFieldFile) -> ImageClass:
    return Image.open(edited_image_url)


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


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    def process_edited_image_form(image_form: EditedImageForm):
        image: ImageFieldFile = image_form.data.get("edited_image_url")
        image_name = format_image_name(image.name)
        image_file = open_image_with_pil(image.path)
        image_size = get_image_size_in_mb(image_file)
        image_resolution = f"{image_file.width}px ⨯ {image_file.height}px"
        image_aspect_ratio: Decimal = Decimal(image_file.width / image_file.height) \
            .quantize(Decimal('.1'), rounding=ROUND_UP)
        return image.url, image_file.format, image_size, image_resolution, image_name, image_aspect_ratio

    user_id = get_user_id(request)
    session_key = get_session_id(request=request)
    edited_image_form: EditedImageForm = EditedImageForm()
    edited_image_format: str = ""
    edited_image_size: str = ""
    edited_image_resolution: str = ""
    edited_image_name: str = ""
    edited_image_url_to_fe: str = ""
    edited_image_aspect_ratio: Decimal = Decimal()

    if request.method == 'POST':
        response = handle_post_request(request, user_id)
    else:
        response = handle_get_request(request, user_id, session_key)

    if isinstance(response, HttpResponsePermanentRedirect) or isinstance(response, HttpResponseRedirect):
        return response

    if isinstance(response, EditedImageForm):
        edited_image_form = response
        edited_image_url_to_fe, edited_image_format, \
            edited_image_size, edited_image_resolution, \
            edited_image_name, edited_image_aspect_ratio = process_edited_image_form(edited_image_form)

    context: dict = {
        'edited_image_form': edited_image_form,
        'edited_image_url_to_fe': edited_image_url_to_fe,
        'edited_image_format': edited_image_format,
        'edited_image_size': edited_image_size,
        'edited_image_resolution': edited_image_resolution,
        'edited_image_name': edited_image_name,
        'edited_image_aspect_ratio': edited_image_aspect_ratio
    }

    return render(request, 'imageEdit.html', context)
