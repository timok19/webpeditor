import logging
import shutil

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.folder_service import create_folder, get_media_root_folder_paths
from webpeditor_app.services.image_services.image_service import get_original_image, get_edited_image, \
    get_image_file_instance
from webpeditor_app.services.image_services.text_utils import replace_with_underscore
from webpeditor_app.services.other_services.session_service import \
    update_image_editor_session, \
    get_user_id_from_session_store, \
    get_or_add_user_id, set_session_expiry

logging.basicConfig(level=logging.INFO)


def clean_up_previous_images(user_id: str) -> HttpResponse | None:
    original_image_folder_path, edited_images_folder_path = get_media_root_folder_paths(user_id)

    previous_original_image = get_original_image(user_id)
    if previous_original_image is None:
        return

    previous_edited_image = get_edited_image(user_id)
    if previous_edited_image is None:
        return

    if original_image_folder_path.exists():
        default_storage.delete(original_image_folder_path / previous_original_image.image_name)
    previous_original_image.delete()

    if edited_images_folder_path.exists():
        shutil.rmtree(edited_images_folder_path)
    previous_edited_image.delete()

    return


def save_uploaded_image_locally(image: UploadedFile, user_id: str) -> str:
    original_user_folder = get_media_root_folder_paths(user_id)[0]
    if not original_user_folder.exists():
        user_folder = create_folder(user_id=user_id, is_original_image=True)
    else:
        user_folder = original_user_folder

    image_name_after_re = replace_with_underscore(image.name)
    uploaded_image_file_path = user_folder / image_name_after_re
    default_storage.save(uploaded_image_file_path, image)

    return f"{user_id}/{image_name_after_re}"


def save_uploaded_image_to_db(image: UploadedFile, original_image: str, request: WSGIRequest, user_id: str):
    original_image = OriginalImage(
        image_name=replace_with_underscore(image.name),
        content_type=image.content_type,
        original_image=original_image,
        session_id=request.session.session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        user_id=user_id
    )
    original_image.save()


def post(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    user_id = get_or_add_user_id(request)

    set_session_expiry(request, 900)

    clean_up_previous_images(user_id)

    form = OriginalImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'imageUpload.html', {'form': form})

    image_file: UploadedFile = form.cleaned_data.get('original_image_form')

    uploaded_image_url = save_uploaded_image_locally(image_file, user_id)
    save_uploaded_image_to_db(image_file, uploaded_image_url, request, user_id)

    update_image_editor_session(request=request, user_id=user_id)

    return redirect('ImageInfoView')


def get(request: WSGIRequest) -> HttpResponse:
    form = OriginalImageForm()
    is_image_exist = True

    user_id = get_user_id_from_session_store(request)

    original_image = get_original_image(user_id)
    if original_image is None:
        is_image_exist = False
    else:
        path_to_original_image = get_image_file_instance(original_image.original_image.path)
        if path_to_original_image is None:
            is_image_exist = False

    context: dict = {
        'form': form,
        'is_image_exist': is_image_exist
    }

    return render(request, 'imageUpload.html', context)


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_upload_view(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    if request.method == 'POST':
        response = post(request)
        return response

    elif request.method == 'GET':
        response = get(request)
        return response

    else:
        return HttpResponse(status=405)
