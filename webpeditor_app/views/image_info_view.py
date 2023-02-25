import os
from pathlib import Path

from PIL import Image
from django.core.exceptions import PermissionDenied

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.session_update import update_session
from webpeditor_app.services.other_services.local_storage import initialize_local_storage


@require_http_methods(['GET'])
def image_info_view(request: WSGIRequest):
    uploaded_image_url = None
    uploaded_image_resolution = None
    uploaded_image_format = None
    uploaded_image_image_name = None
    uploaded_image_aspect_ratio = None
    uploaded_image_size = None
    local_storage = initialize_local_storage()

    if request.method == 'GET':
        user_id = request.session.get('user_id')
        uploaded_image = OriginalImage.objects.filter(user_id=user_id).first()

        if not uploaded_image:
            return redirect("ImageDoesNotExistView")
        if uploaded_image.user_id != user_id:
            raise PermissionDenied("You do not have permission to view this image.")

        uploaded_image_url = local_storage.getItem("image_url")
        path_to_local_image: Path = settings.MEDIA_ROOT / uploaded_image.user_id / uploaded_image.image_file

        try:
            image_local_file = Image.open(path_to_local_image)
        except FileExistsError or FileNotFoundError:
            return redirect("ImageDoesNotExistView")

        # Image format
        uploaded_image_format = ".{}".format(image_local_file.format)

        # Image resolution
        uploaded_image_resolution = "{}px ⨯ {}px".format(image_local_file.size[0], image_local_file.size[1])

        # Image name
        basename, ext = os.path.splitext(uploaded_image.image_file)
        if len(basename) > 20:
            basename = basename[:17] + "..."
            uploaded_image_image_name = basename + ext
        else:
            uploaded_image_image_name = uploaded_image.image_file

        # Image aspect ratio
        uploaded_image_aspect_ratio = round(image_local_file.width / image_local_file.height, 1)

        # Image size
        size = round(os.path.getsize(path_to_local_image) / 1024, 2)
        uploaded_image_size = "{} KB".format(size)

        if size > 1000:
            size /= 1024
            uploaded_image_size = "{} MB".format(round(size, 2))

        update_session(request=request, user_id=user_id)

    return render(request, 'imageInfo.html',
                  {
                      'uploaded_image_url': uploaded_image_url,
                      'image_format': uploaded_image_format,
                      'image_resolution': uploaded_image_resolution,
                      'image_name': uploaded_image_image_name,
                      'aspect_ratio': uploaded_image_aspect_ratio,
                      'image_size': uploaded_image_size
                   })
