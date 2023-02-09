from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage, default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.models.database.serializers import OriginalImageSerializer
from webpeditor_app.services.image_services.re_for_file_name import replace_with_underscore
from webpeditor_app.services.session_id_to_db import set_session_expiry, update_session
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


@csrf_exempt
def upload_image_view(request: WSGIRequest):
    set_session_expiry(request)

    if request.method != 'POST':
        image_form = OriginalImageForm()
    else:
        image_form = OriginalImageForm(request.POST, request.FILES)

        if not image_form.is_valid():
            return redirect('MainPage')
        else:
            previous_image = OriginalImage.objects.filter(session_id=request.session.session_key).first()
            if previous_image:
                default_storage.delete(previous_image.original_image_url.name)
                previous_image.delete()

            image: UploadedFile = image_form.cleaned_data['image']

            try:
                validate_image_file_size(image)
            except ValidationError as error:
                print("Error: " + str(error))

            image_name_after_re: str = replace_with_underscore(image.name)
            image_file: DefaultStorage = default_storage.save(image_name_after_re, image)

            original_image_object = OriginalImage(image_file=image_file,
                                                  content_type=image.content_type,
                                                  original_image_url=image_name_after_re,
                                                  session_id=request.session.session_key)
            original_image_object.save()

            update_session(request, request.session.session_key)

            return redirect('MainPage')

    return render(request, 'index.html', {'form': image_form})


# TODO: add page with binding (image_info/) for getting information about added image (image itself, size in KB,
#  resolution, ratio, format)
@csrf_exempt
def show_image_view(request: WSGIRequest):
    if request.method == 'GET':
        original_images = OriginalImage.objects.all()
        original_image_serializer = OriginalImageSerializer(original_images, many=True)

        return redirect('MainPage')
    return render(request, 'index.html', {})
