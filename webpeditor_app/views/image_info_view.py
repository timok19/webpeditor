import os
from pathlib import Path

from PIL import Image

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render

from webpeditor import settings
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.session_id_to_db import update_session


def image_info_view(request: WSGIRequest):
    uploaded_image_url = None
    uploaded_image_resolution = None
    uploaded_image_format = None
    uploaded_image_image_name = None
    uploaded_image_aspect_ratio = None
    uploaded_image_size = None

    if request.method == 'GET':
        uploaded_image = OriginalImage.objects.filter(session_id=request.session.session_key).first()

        if not uploaded_image:
            return redirect("ImageDoesNotExistView")

        uploaded_image_url = uploaded_image.original_image_url.url
        path_to_local_image: Path = settings.MEDIA_ROOT / request.session.session_key / uploaded_image.image_file

        image_local_file = Image.open(path_to_local_image)

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

        update_session(request.session.session_key)

    return render(request, 'imageInfo.html', {'uploaded_image_url': uploaded_image_url,
                                              'session_id': request.session.session_key,
                                              'image_format': uploaded_image_format,
                                              'image_resolution': uploaded_image_resolution,
                                              'image_name': uploaded_image_image_name,
                                              'aspect_ratio': uploaded_image_aspect_ratio,
                                              'image_size': uploaded_image_size})
