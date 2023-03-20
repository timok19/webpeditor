import uuid

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_name_service import replace_with_underscore
from webpeditor_app.services.image_services.user_folder_service import create_new_folder
from webpeditor_app.services.other_services.session_service import set_session_expiry, update_session
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


def handle_request_user_id(request: WSGIRequest) -> str:
    try:
        return request.session['user_id']
    except KeyError:
        request.session['user_id'] = str(uuid.uuid4())
        return request.session['user_id']


def handle_previous_image_deletion(user_id: str):
    previous_image = OriginalImage.objects.filter(user_id=user_id).first()
    if not previous_image:
        return

    user_folder = create_new_folder(user_id=user_id, uploaded_image_folder_status=True)
    default_storage.delete(user_folder / previous_image.image_name)
    previous_image.delete()

    try:
        # Delete image in "edited" folder if user is uploading a new one
        path_to_edited_image = user_folder / 'edited' / previous_image.image_name
        if path_to_edited_image.exists():
            default_storage.delete(path_to_edited_image)
    except Exception as e:
        print(e)
        pass


def save_uploaded_image(image: UploadedFile, user_id: str) -> str:
    user_folder = create_new_folder(user_id=user_id, uploaded_image_folder_status=True)
    image_name_after_re = replace_with_underscore(image.name)
    uploaded_image_path_to_local = user_folder / image_name_after_re
    default_storage.save(uploaded_image_path_to_local, image)
    return f"{user_id}/{image_name_after_re}"


def create_and_save_original_image(image: UploadedFile, image_url: str, request: WSGIRequest, user_id: str):
    original_image = OriginalImage(
        image_name=replace_with_underscore(image.name),
        content_type=image.content_type,
        original_image_url=image_url,
        session_id=request.session.session_key,
        session_id_expiration_date=request.session.get_expiry_date(),
        user_id=user_id
    )
    original_image.save()


@csrf_protect
@require_http_methods(['POST', 'GET'])
def image_upload_view(request: WSGIRequest):
    uploaded_image_url_to_fe = ""
    original_image = None
    set_session_expiry(request)

    if request.method == 'POST':
        user_id = handle_request_user_id(request)

        handle_previous_image_deletion(user_id)

        image_form = OriginalImageForm(request.POST, request.FILES)

        if not image_form.is_valid():
            return redirect('UploadImageView')

        image: UploadedFile = image_form.cleaned_data['original_image_form']

        try:
            validate_image_file_size(image)
        except ValidationError as errors:
            error_str = "".join(str(error) for error in errors)
            return render(request, 'imageUpload.html', {'form': image_form, 'validation_error': error_str})

        uploaded_image_url_to_fe = save_uploaded_image(image, user_id)

        create_and_save_original_image(image, uploaded_image_url_to_fe, request, user_id)

        update_session(request=request, user_id=user_id)

        return redirect('ImageInfoView')

    else:
        image_form = OriginalImageForm()
        user_id = None
        image_is_exist = True

        try:
            user_id = request.session['user_id']
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
