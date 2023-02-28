from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.crypto import get_random_string

from webpeditor_app.models.database.forms import OriginalImageForm
from webpeditor_app.models.database.models import OriginalImage
from webpeditor_app.services.image_services.image_convert import convert_url_to_base64
from webpeditor_app.services.other_services.session_services import set_session_expiry, update_session
from webpeditor_app.services.image_services.user_folder import create_new_folder
from webpeditor_app.services.image_services.re_for_file_name import replace_with_underscore
from webpeditor_app.services.other_services.local_storage import initialize_local_storage, save_to_local_storage
from webpeditor_app.services.validators.image_size_validator import validate_image_file_size


@csrf_protect
@require_http_methods(['POST', 'GET'])
def image_upload_view(request: WSGIRequest):
    image_is_exist: bool = True
    image_url_in_local_storage: str = ""
    local_storage = initialize_local_storage()
    set_session_expiry(request)

    if request.method == 'POST':
        created_user_id = request.session.get('user_id')
        if created_user_id is None:
            request.session['user_id'] = get_random_string(length=32)
            created_user_id = request.session.get('user_id')

        user_folder: Path = create_new_folder(user_id=created_user_id, uploaded_image_folder_status=True)

        previous_image = OriginalImage.objects.filter(user_id=created_user_id).first()
        if previous_image:
            default_storage.delete(user_folder / previous_image.image_file)
            previous_image.delete()
            try:
                # Delete image in "edited" folder if user is uploading a new one
                path_to_edited_image = user_folder / 'edited' / previous_image.image_file
                if path_to_edited_image.exists():
                    default_storage.delete(path_to_edited_image)
            except Exception as e:
                print(e)
                pass

        image_form = OriginalImageForm(request.POST, request.FILES)

        if not image_form.is_valid():
            return redirect('UploadImageView')

        image: UploadedFile = image_form.cleaned_data['image']

        try:
            validate_image_file_size(image)
        except ValidationError as errors:
            error_str = ""
            for error in errors:
                error_str += str(error)

            return render(request, 'imageUpload.html',
                          {
                              'form': image_form,
                              'validation_error': error_str
                          })

        image_name_after_re: str = replace_with_underscore(image.name)

        uploaded_image_path_to_local = user_folder / image_name_after_re
        default_storage.save(uploaded_image_path_to_local, image)

        uploaded_image_path_to_db = str(created_user_id + "/" + image_name_after_re)
        original_image = OriginalImage(image_file=image_name_after_re,
                                       content_type=image.content_type,
                                       original_image_url=uploaded_image_path_to_db,
                                       session_id_expiration_date=request.session.get_expiry_date(),
                                       user_id=created_user_id)
        original_image.save()

        uploaded_image_path_to_fe = convert_url_to_base64(uploaded_image_path_to_local, image.content_type)
        save_to_local_storage(local_storage, uploaded_image_path_to_fe)

        update_session(request=request, user_id=created_user_id)

        return redirect('ImageInfoView')

    else:
        image_form = OriginalImageForm()
        created_user_id = request.session.get('user_id')
        original_image = OriginalImage.objects.filter(user_id=created_user_id).first()

        if original_image:
            image_url_in_local_storage = local_storage.getItem("image_url")

        update_session(request=request, user_id=created_user_id)

    return render(request, 'imageUpload.html',
                  {
                      'form': image_form,
                      'original_image': original_image,
                      'image_url_in_local_storage': image_url_in_local_storage,
                      'image_is_exist': image_is_exist
                  })
