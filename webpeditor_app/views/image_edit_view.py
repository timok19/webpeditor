from pathlib import Path

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.forms import EditedImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.user_folder import create_new_folder
from webpeditor_app.services.other_services.local_storage import initialize_local_storage


@csrf_protect
@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    local_storage = initialize_local_storage()
    uploaded_image_url = None

    if request.method == 'POST':
        valid_user_id = request.session.get('user_id')
        if valid_user_id is None:
            return redirect('ImageDoesNotExistView')

        user_edited_image: Path = create_new_folder(user_id=valid_user_id, uploaded_image_folder_status=False)

        edited_image_form = EditedImageForm(request.POST, request.FILES)
        if edited_image_form.is_valid():
            edited_image_form.save()
            return redirect('ImageEditView')

    if request.method == 'GET':
        user_id = request.session.get('user_id')

        image = OriginalImage.objects.filter(user_id=user_id).first()
        if not image:
            return redirect("ImageDoesNotExistView")

        uploaded_image_url = local_storage.getItem("image_url")

    return render(request, 'imageEditView/imageEdit.html',
                  {'uploaded_image_url': uploaded_image_url, })
