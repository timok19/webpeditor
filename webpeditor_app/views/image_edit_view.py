import shutil

from django.core.files.storage import FileSystemStorage
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor import settings
from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.user_folder_service import create_new_folder
from webpeditor_app.services.other_services.session_service import update_session, get_session_id


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
    original_image_path_to_local = settings.MEDIA_ROOT / user_id
    edited_image_path_to_local = original_image_path_to_local / 'edited'
    storage = FileSystemStorage()

    if not edited_image_path_to_local.exists():
        edited_image_path_to_local = create_new_folder(user_id=user_id, uploaded_image_folder_status=False)

    original_image_file_path = original_image_path_to_local / original_image.image_name
    edited_image_file_path = edited_image_path_to_local / edited_image.edited_image_name
    shutil.copy2(original_image_file_path, edited_image_file_path)

    file = storage.open(
        name=f"{settings.MEDIA_ROOT}/{user_id}/edited/{edited_image.edited_image_name}"
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


def handle_post_request(request: WSGIRequest, user_id: str, session_key: str):
    ###
    print(session_key)
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
    if edited_image is None and original_image.user_id == user_id:
        edited_image = create_and_save_edited_image(user_id, original_image, session_key, request)

        if not copy_original_image_to_edited_folder(user_id, original_image, edited_image):
            return redirect("ImageDoesNotExistView")

        edited_image_form: EditedImageForm = create_edited_image_form(edited_image)
    else:
        return redirect('ImageDoesNotExistView')

    update_session(request=request, user_id=user_id)

    return edited_image_form


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    user_id = get_user_id(request)
    session_key = get_session_id(request=request)
    edited_image_url_to_fe = ""
    edited_image_form: EditedImageForm = EditedImageForm()

    if request.method == 'POST':
        response = handle_post_request(request, user_id, session_key)
        if isinstance(response, EditedImageForm):
            edited_image_form = response
            edited_image_url = edited_image_form.data.get("edited_image_url")
            edited_image_url_to_fe = f"/media/{edited_image_url}"
    else:
        response = handle_get_request(request, user_id, session_key)
        if isinstance(response, HttpResponsePermanentRedirect) or isinstance(response, HttpResponseRedirect):
            return response

        if isinstance(response, EditedImageForm):
            edited_image_form = response
            edited_image_url = edited_image_form.data.get("edited_image_url")
            edited_image_url_to_fe = f"/media/{edited_image_url}"

    context: dict = {
        'edited_image_form': edited_image_form,
        'edited_image_url_to_fe': edited_image_url_to_fe
    }

    return render(request, 'imageEdit.html', context)
