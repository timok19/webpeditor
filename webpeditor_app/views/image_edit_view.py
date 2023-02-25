import shutil

from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor import settings
from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage, EditedImage
from webpeditor_app.services.image_services.session_update import update_session
from webpeditor_app.services.image_services.user_folder import create_new_folder
from webpeditor_app.services.other_services.local_storage import initialize_local_storage


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    user_id = request.session.get('user_id')
    local_storage = initialize_local_storage()
    uploaded_image_url = ""
    edited_image_url = ""

    original_image_path_to_local = settings.MEDIA_ROOT / user_id
    edited_image_path_to_local = original_image_path_to_local / 'edited'

    if request.method == 'POST':
        if user_id is None:
            return redirect('ImageDoesNotExistView')

        edited_image_form = EditedImageForm(request.POST, request.FILES)
        if edited_image_form.is_valid():
            edited_image_form.save()
            return redirect('ImageEditView')

        update_session(request=request, user_id=user_id)

    else:
        if user_id is None:
            return redirect('ImageDoesNotExistView')

        uploaded_image = OriginalImage.objects.filter(user_id=user_id).first()
        if not uploaded_image:
            return redirect("ImageDoesNotExistView")
        if uploaded_image.user_id != user_id:
            raise PermissionDenied("You do not have permission to view this image.")

        if not edited_image_path_to_local.exists():
            edited_image_path_to_local = create_new_folder(user_id=user_id, uploaded_image_folder_status=False)

        # Copy original image and paste it into "edited" folder
        original_image_file_path = original_image_path_to_local / uploaded_image.image_file
        edited_image_file_path = edited_image_path_to_local / uploaded_image.image_file
        shutil.copy2(original_image_file_path, edited_image_file_path)

        try:
            previously_opened_image = EditedImage.objects.filter(user_id=user_id).first()
            if previously_opened_image:
                edited_image_url = local_storage.getItem("edited_image_url")
            else:
                uploaded_image_url = local_storage.getItem("image_url")

        except EditedImage.DoesNotExist as e:
            print(e)

        # update_session(session_id=request.session.session_key, user_id=user_id)
        edited_image_form = EditedImageForm()
        update_session(request=request, user_id=user_id)

    return render(request, 'imageEdit.html',
                  {
                      'edited_image_form': edited_image_form,
                      'uploaded_image_url': uploaded_image_url,
                      'edited_image_url': edited_image_url
                  })
