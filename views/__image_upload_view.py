from typing import Tuple

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from PIL.Image import Image as ImageClass


def clean_up_previous_images(user_id: str):
    ...
    # previous_original_image: EditorOriginalImageAsset | None = get_original_image(user_id)
    # if isinstance(previous_original_image, EditorOriginalImageAsset):
    #     previous_original_image.delete()
    #
    # delete_cloudinary_original_and_edited_images(user_id)


def upload_original_image_to_cloudinary(image: InMemoryUploadedFile, user_id: str) -> Tuple[str, str]:
    ...
    # folder_path: str = f"{user_id}/"
    #
    # image_name: str = get_image_file_name(str(image.name))
    # # image_name_after_re: str = FileUtils.normalize_filename(image_name)
    # new_original_image_name: str = f"webpeditor_{image_name_after_re}"
    #
    # cloudinary_parameters: dict = {
    #     "folder": folder_path,
    #     "use_filename": True,
    #     "unique_filename": False,
    #     "filename_override": new_original_image_name,
    #     "overwrite": True,
    # }
    # cloudinary_image = cloudinary.uploader.upload_image(image, **cloudinary_parameters)
    #
    # return cloudinary_image.url, new_original_image_name


def original_image_exist(request: WSGIRequest) -> bool:
    ...
    # user_id: str | None = get_unsigned_user_id(request)
    # original_image: EditorOriginalImageAsset | None = get_original_image(user_id)  # pyright: ignore [reportArgumentType]
    #
    # if original_image is None:
    #     return False
    #
    # return True


def handle_user_session(request: WSGIRequest) -> str:
    ...
    # user_id = get_unsigned_user_id(request)
    # if user_id is None:
    #     add_signed_user_id_to_session_store(request)
    #     user_id = get_unsigned_user_id(request)
    # set_session_expiry(request, 900)
    #
    # return user_id  # pyright: ignore [reportReturnType]


def handle_image_upload(request: WSGIRequest) -> HttpResponse | tuple[InMemoryUploadedFile, ImageClass]:
    ...
    # form = OriginalImageAssetForm(request.POST, request.FILES)
    # if not form.is_valid():
    #     context: dict = {
    #         "error": "Unknown file format",
    #         "original_image_exist": original_image_exist(request),
    #     }
    #     return render(request, "webpeditor_app/image-uploader.html", context, status=200)
    #
    # uploaded_original_image_file: InMemoryUploadedFile = request.FILES["original_image_form"]  # pyright: ignore [reportAssignmentType]
    # image: ImageClass = PilImage.open(uploaded_original_image_file)
    #
    # return uploaded_original_image_file, image


def check_image_constraints(
    request: WSGIRequest,
    image: ImageClass,
    uploaded_original_image_file: InMemoryUploadedFile,
) -> None | HttpResponse:
    ...
    # are_image_dimensions_more: bool = image.width > 2500 or image.height > 2500
    # is_image_file_size_more: bool = uploaded_original_image_file.size > MAX_IMAGE_FILE_SIZE  # pyright: ignore [reportOptionalOperand]
    # if is_image_file_size_more or are_image_dimensions_more:
    #     context: dict = {
    #         "error": f"Image should not exceed {MAX_IMAGE_FILE_SIZE / 1_000_000} MB"
    #         if is_image_file_size_more
    #         else "Image dimensions should not be more than 2500x2500px",
    #         "original_image_exist": original_image_exist(request),
    #     }
    #     return render(request, "webpeditor_app/image-uploader.html", context)
    #
    # return None


def save_original_image(
    user_id: str,
    new_image_name: str,
    uploaded_original_image_file: InMemoryUploadedFile,
    cloudinary_image_url: str,
    request: WSGIRequest,
) -> None:
    ...
    # original_image: EditorOriginalImageAsset = EditorOriginalImageAsset(
    #     user_id=user_id,
    #     image_name=new_image_name,
    #     content_type=uploaded_original_image_file.content_type,
    #     image_url=cloudinary_image_url,
    #     session_key=request.session.session_key,
    #     session_key_expiration_date=request.session.get_expiry_date(),
    # )
    #
    # original_image.save()


def post(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    ...
    # user_id: str = handle_user_session(request)
    #
    # clean_up_previous_images(user_id)
    #
    # if "original_image_form" not in request.FILES:
    #     context: dict = {
    #         "error": "No image file was provided.",
    #         "original_image_exist": original_image_exist(request),
    #     }
    #     return render(request, "webpeditor_app/image-uploader.html", context)
    #
    # response: HttpResponse | tuple[InMemoryUploadedFile, Image] = handle_image_upload(request)
    #
    # if isinstance(response, HttpResponse):
    #     return response
    #
    # uploaded_original_image_file: InMemoryUploadedFile = response[0]
    # image: ImageClass = response[1]
    #
    # constraints_response: HttpResponse | None = check_image_constraints(request, image, uploaded_original_image_file)
    #
    # if isinstance(constraints_response, HttpResponse):
    #     return constraints_response
    #
    # uploaded_original_image_file.seek(0)
    # cloudinary_image_url, new_image_name = upload_original_image_to_cloudinary(uploaded_original_image_file, user_id)
    #
    # save_original_image(
    #     user_id,
    #     new_image_name,
    #     uploaded_original_image_file,
    #     cloudinary_image_url,
    #     request,
    # )
    #
    # image.close()
    #
    # update_session(request=request, user_id=user_id)
    #
    # return redirect("image-info-view")


def get(request: WSGIRequest) -> HttpResponse:
    ...
    # return render(
    #     request,
    #     "webpeditor_app/image-uploader.html",
    #     context={
    #         "form": OriginalImageAssetForm(),
    #         "original_image_exist": original_image_exist(request),
    #     },
    #     status=200,
    # )


@csrf_protect
@require_http_methods(["GET", "POST"])
def image_upload_view(request: WSGIRequest) -> HttpResponse | HttpResponsePermanentRedirect | HttpResponseRedirect:
    ...
    # if request.method == "POST":
    #     return post(request)
    #
    # return get(request)
