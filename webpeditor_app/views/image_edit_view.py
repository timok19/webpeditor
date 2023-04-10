import logging

from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_service import \
    get_original_image, \
    get_edited_image, \
    copy_original_image_to_edited_folder, \
    get_image_file_instance, \
    get_info_about_image
from webpeditor_app.services.other_services.session_service import \
    update_image_editor_session, \
    get_session_id, \
    get_user_id_from_session_store
from webpeditor_app.views.image_info_view import format_image_file_name

logging.basicConfig(level=logging.INFO)


def create_and_save_edited_image(user_id: str,
                                 original_image: OriginalImage,
                                 session_key: str,
                                 request: WSGIRequest) -> EditedImage:
    new_edited_image_name = f"webpeditor_{original_image.image_name}"
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


def get(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    user_id = get_user_id_from_session_store(request)
    if user_id is None:
        return redirect('ImageDoesNotExistView')

    original_image = get_original_image(user_id)
    if original_image is None:
        return redirect("ImageDoesNotExistView")

    if original_image.user_id != user_id:
        raise PermissionDenied("You do not have permission to view this image.")

    original_image_file = get_image_file_instance(original_image.original_image.path)
    if original_image_file is None:
        return redirect("ImageDoesNotExistView")

    original_image_format_description = original_image_file.format_description

    session_key = get_session_id(request)

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

    image: EditedImage = edited_image_form.data.get("edited_image")

    image_name = format_image_file_name(image.edited_image_name)

    context: dict = {
        'edited_image_url': str(image.edited_image.url),
        'edited_image_name_short_version': image_name,
        'edited_image_size': get_info_about_image(image.edited_image.path)[1],
        'edited_image_resolution': get_info_about_image(image.edited_image.path)[2],
        'edited_image_aspect_ratio': get_info_about_image(image.edited_image.path)[3],
        'edited_image_format': original_image_format_description,
        'edited_image_mode': get_info_about_image(original_image.original_image.path)[4],
        'edited_image_exif_data': get_info_about_image(original_image.original_image.path)[5],
        'edited_image_metadata': get_info_about_image(original_image.original_image.path)[6],
        'image_form': edited_image_form,
        'edited_image_name': image.edited_image_name,
        'csrf_token_value': get_token(request),
        'edited_image_content_type': edited_image.content_type_edited
    }

    original_image_file.close()

    update_image_editor_session(request=request, user_id=user_id)

    return render(request, 'imageEdit.html', context)


@requires_csrf_token
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    if request.method == "GET":
        response = get(request)
        return response

    else:
        return HttpResponse(status=405)
