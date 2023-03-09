import shutil

from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor import settings
from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.image_convert import convert_url_to_base64
from webpeditor_app.services.image_services.user_folder import create_new_folder
from webpeditor_app.services.other_services.session_service import update_session


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    try:
        user_id = request.session['user_id']
    except Exception as e:
        print(e)
        return redirect('UploadImageView')

    session_key = request.session.session_key
    edited_image_url = ""

    original_image_path_to_local = settings.MEDIA_ROOT / user_id
    edited_image_path_to_local = original_image_path_to_local / 'edited'

    if request.method == 'POST':
        if request.session.get_expiry_age() == 0:
            return redirect('ImageDoesNotExistView')

        if user_id is None:
            return redirect('ImageDoesNotExistView')

        edited_image_form = EditedImageForm(request.POST)

        if not edited_image_form.is_valid():
            return JsonResponse({"message": "Image not cropped and saved",
                                 "error": edited_image_form.errors})

        edited_image = edited_image_form.cleaned_data.get('image')
        print(edited_image)

        edited_image_path_to_fe = request.session.get('edited_image_url')

        update_session(request=request, user_id=user_id)

    elif request.method == 'GET':
        if user_id is None:
            return redirect('ImageDoesNotExistView')

        try:
            uploaded_image = OriginalImage.objects.filter(user_id=user_id).first()
        except OriginalImage.DoesNotExist:
            return redirect("ImageDoesNotExistView")

        if uploaded_image.user_id != user_id:
            raise PermissionDenied("You do not have permission to view this image.")

        if not edited_image_path_to_local.exists():
            edited_image_path_to_local = create_new_folder(user_id=user_id, uploaded_image_folder_status=False)

        # Copy original image and paste it into "edited" folder
        original_image_file_path = original_image_path_to_local / uploaded_image.image_file
        edited_image_file_path = edited_image_path_to_local / uploaded_image.image_file
        shutil.copy2(original_image_file_path, edited_image_file_path)

        # Convert edited image to base64
        if edited_image_file_path:
            edited_image_path_to_fe = convert_url_to_base64(edited_image_file_path, uploaded_image.content_type)
            request.session['edited_image_url'] = edited_image_path_to_fe
            edited_image_url = request.session.get('edited_image_url')

        uploaded_image_path_to_db = f"{user_id}/edited/{uploaded_image.image_file}"
        edited_image = EditedImage(user_id=user_id,
                                   edited_image_url=uploaded_image_path_to_db,
                                   edited_image_file=uploaded_image.image_file,
                                   content_type_edited=uploaded_image.content_type,
                                   session_id=session_key,
                                   session_id_expiration_date=request.session.get_expiry_date(),
                                   original_image_file_id=uploaded_image.image_id
                                   )
        edited_image.save()

        try:
            edited_image = EditedImage.objects.filter(user_id=user_id).first()
        except EditedImage.DoesNotExist as e:
            print(e)

        edited_image_form = EditedImageForm()
        update_session(request=request, user_id=user_id)

    else:
        edited_image_form = EditedImageForm()

    return render(request, 'imageEdit.html',
                  {
                      'edited_image_form': edited_image_form,
                      'edited_image_url': edited_image_url
                  })
