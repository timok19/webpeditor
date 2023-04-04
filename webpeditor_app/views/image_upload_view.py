import shutil
import uuid

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.folder_service import create_folder, get_media_root_paths
from webpeditor_app.services.image_services.text_utils import replace_with_underscore
from webpeditor_app.services.other_services.session_service import set_session_expiry, update_session

uploaded_image_url_to_fe: str = ""


def get_or_create_user_id(request: WSGIRequest) -> str:
    try:
        return request.session['user_id']
    except KeyError:
        request.session['user_id'] = str(uuid.uuid4())
        return request.session['user_id']


def validate_previous_image(user_id: str):
    original_image_folder_path, edited_images_folder_path = get_media_root_paths(user_id)

    previous_original_image = OriginalImage.objects.filter(user_id=user_id).first()
    if not previous_original_image:
        return

    previous_edited_image = EditedImage.objects.filter(user_id=user_id).all()
    if not previous_original_image:
        return

    try:
        if original_image_folder_path.exists():
            default_storage.delete(original_image_folder_path / previous_original_image.image_name)
        previous_original_image.delete()
    except Exception as e:
        print(e)

    try:
        if edited_images_folder_path.exists():
            shutil.rmtree(edited_images_folder_path)
        previous_edited_image.delete()
    except Exception as e:
        print(e)


def save_image_locally(image: UploadedFile, user_id: str) -> str:
    original_user_folder, _ = get_media_root_paths(user_id)
    if not original_user_folder.exists():
        user_folder = create_folder(user_id=user_id, is_original_image=True)
    else:
        user_folder = original_user_folder

    image_name_after_re = replace_with_underscore(image.name)
    uploaded_image_path_to_local = user_folder / image_name_after_re
    default_storage.save(uploaded_image_path_to_local, image)

    return f"{user_id}/{image_name_after_re}"


def save_image_to_db(image: UploadedFile, original_image: str, request: WSGIRequest, user_id: str):
    original_image = OriginalImage(
        image_name=replace_with_underscore(image.name),
        content_type=image.content_type,
        original_image=original_image,
        session_id=request.session.session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        user_id=user_id
    )
    original_image.save()


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_upload_view(request: WSGIRequest):
    global uploaded_image_url_to_fe

    if request.method == 'POST':
        set_session_expiry(request)

        user_id = get_or_create_user_id(request)
        validate_previous_image(user_id)

        image_form = OriginalImageForm(request.POST, request.FILES)
        if not image_form.is_valid():
            return render(request, 'imageUpload.html', {'form': image_form})

        image: UploadedFile = image_form.cleaned_data.get('original_image_form')

        uploaded_image_url_to_fe = save_image_locally(image, user_id)

        save_image_to_db(image, uploaded_image_url_to_fe, request, user_id)

        update_session(request=request, user_id=user_id)

        return redirect('ImageInfoView')

    elif request.method == 'GET':
        image_form = OriginalImageForm()
        original_image = None
        user_id = None
        image_is_exist = True

        try:
            user_id = request.session.get('user_id')
        except KeyError:
            image_is_exist = False

        try:
            original_image = OriginalImage.objects.filter(user_id=user_id).first()
        except OriginalImage.DoesNotExist:
            image_is_exist = False

        context: dict = {
            'form': image_form,
            'original_image': original_image,
            'uploaded_image_url_to_fe': uploaded_image_url_to_fe,
            'image_is_exist': image_is_exist
        }

        return render(request, 'imageUpload.html', context)

    else:
        return HttpResponse(status=405)
