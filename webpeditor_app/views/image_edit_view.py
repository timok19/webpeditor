from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from webpeditor_app.models.database.models import OriginalImage


@require_http_methods(['GET', 'POST'])
def image_edit_view(request: WSGIRequest):
    uploaded_image_url = None
    if request.method == 'GET':
        user_id = request.session.get('user_id')

        image = OriginalImage.objects.filter(user_id=user_id).first()
        if not image:
            return redirect("ImageDoesNotExistView")

        uploaded_image_url = image.original_image_url.url

    return render(request, 'imageEdit.html', {'uploaded_image_url': uploaded_image_url})
