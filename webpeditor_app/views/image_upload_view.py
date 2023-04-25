import logging
import cloudinary.uploader
import cloudinary.api

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor.settings import MAX_IMAGE_FILE_SIZE
from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_service import get_original_image, get_edited_image
from webpeditor_app.services.image_services.text_utils import replace_with_underscore
from webpeditor_app.services.other_services.session_service import \
    update_image_editor_session, \
    get_user_id_from_session_store, \
    get_or_add_user_id, set_session_expiry

logging.basicConfig(level=logging.INFO)


# cloudinary.uploader.destroy(cloudinary_image.public_id)
# cloudinary.api.delete_folder(folder_path)
# result = cloudinary.uploader\
# .rename("canyon", "grand_canyon") -> for file renaming

def clean_up_previous_images(user_id: str) -> None:
    previous_original_image = get_original_image(user_id)
    previous_edited_image = get_edited_image(user_id)
    if previous_original_image is None or previous_edited_image is None:
        return None

    # TODO: add deletion of previous images on Cloudinary
    previous_original_image.delete()
    previous_edited_image.delete()


def upload_image_to_cloudinary(image: InMemoryUploadedFile, user_id: str) -> str:
    folder_path: str = f"{user_id}/"
    cloudinary_image = cloudinary.uploader.upload_image(
        file=image,
        folder=folder_path,
        use_filename=True,
        overwrite=True
    )

    return cloudinary_image.url


def save_uploaded_image_to_db(image_file: InMemoryUploadedFile, image_url: str, request: WSGIRequest, user_id: str):
    image_url = OriginalImage(
        image_name=replace_with_underscore(image_file.name),
        content_type=image_file.content_type,
        image_url=image_url,
        session_id=request.session.session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        user_id=user_id
    )
    image_url.save()


def post(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    user_id = get_or_add_user_id(request)

    set_session_expiry(request, 900)

    clean_up_previous_images(user_id)

    uploaded_image_file: InMemoryUploadedFile = request.FILES['original_image_form']
    if uploaded_image_file.size > MAX_IMAGE_FILE_SIZE:
        max_image_file_size_in_mb = MAX_IMAGE_FILE_SIZE / 1_000_000
        return render(request, 'imageUpload.html', {'error': f'Image should not exceed {max_image_file_size_in_mb}'})

    uploaded_image_url = upload_image_to_cloudinary(uploaded_image_file, user_id)
    save_uploaded_image_to_db(uploaded_image_file, uploaded_image_url, request, user_id)

    update_image_editor_session(request=request, user_id=user_id)

    return redirect('ImageInfoView')


def get(request: WSGIRequest) -> HttpResponse:
    form = OriginalImageForm()
    is_image_exist = True

    user_id = get_user_id_from_session_store(request)

    original_image = get_original_image(user_id)
    if original_image is None or original_image.image_url is None:
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
