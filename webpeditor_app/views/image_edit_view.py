from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.other_services.local_storage import initialize_local_storage


@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    local_storage = initialize_local_storage()
    uploaded_image_url = None

    if request.method == 'GET':
        user_id = request.session.get('user_id')

        image = OriginalImage.objects.filter(user_id=user_id).first()
        if not image:
            return redirect("ImageDoesNotExistView")

        uploaded_image_url = local_storage.getItem("image_url")

    return render(request, 'imageEdit.html', {'uploaded_image_url': uploaded_image_url})
