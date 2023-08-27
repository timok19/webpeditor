import logging
from uuid import UUID

from PIL.Image import Image, open
from asgiref.sync import sync_to_async

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from webpeditor.settings import MAX_IMAGE_FILE_SIZE
from webpeditor_app.database.models.original_image_model import (
    OriginalImage,
    ImageModel,
)
from webpeditor_app.forms.forms import OriginalImageForm
from webpeditor_app.commands.original_images_commands import OriginalImagesCommands
from webpeditor_app.services.image_services.image_editor_service import (
    get_image_file_name,
)
from webpeditor_app.utils.text_utils import replace_with_underscore
from webpeditor_app.services.other_services.session_service import SessionService
from webpeditor_app.services.other_services.cloudinary_service import CloudinaryService
from webpeditor_app.views.view_utils.get_user_data import async_csrf_protect


class ImageUploadView(View):
    logging.basicConfig(level=logging.INFO)

    async_csrf_protect_method = method_decorator(async_csrf_protect)

    session_service: SessionService | None = None
    original_images_commands: OriginalImagesCommands | None = None

    user_id: UUID | None = None
    original_image: OriginalImage | None = None
    previous_original_image: OriginalImage | None = None

    uploaded_original_image_file: InMemoryUploadedFile | None = None
    image: Image | None = None

    cloudinary_image_url: str | None = None
    new_image_name: str | None = None

    @sync_to_async
    def handle_user_session(self, request: ASGIRequest):
        self.session_service = SessionService(request=request)
        self.session_service.get_unsigned_user_id()

        if self.session_service.user_id is None:
            self.session_service.add_new_signed_user_id_to_session_store()
            self.session_service.get_unsigned_user_id()
            self.user_id = self.session_service.user_id

        self.session_service.set_session_expiry(900)

    async def clean_up_previous_images(self):
        self.previous_original_image: OriginalImage | None = (
            await self.original_images_commands.get_original_image()
        )
        if self.previous_original_image is not None:
            await self.previous_original_image.delete()

        CloudinaryService.delete_original_and_edited_images(self.user_id.__str__())

    @sync_to_async
    def upload_original_image_to_cloudinary(self, image_file: InMemoryUploadedFile):
        folder_path: str = f"{self.user_id.__str__()}/"

        image_name: str = get_image_file_name(str(image_file.name))
        image_name_after_re: str = replace_with_underscore(image_name)
        new_original_image_name: str = f"webpeditor_{image_name_after_re}"

        cloudinary_image = CloudinaryService.upload_image(
            file=image_file,
            parameters={
                "folder": folder_path,
                "use_filename": True,
                "unique_filename": False,
                "filename_override": new_original_image_name,
                "overwrite": True,
            },
        )

        self.new_image_name = new_original_image_name
        self.cloudinary_image_url = cloudinary_image.url

    async def check_image_existence(self):
        original_image = await self.original_images_commands.get_original_image()

        return True if original_image is not None else False

    @sync_to_async
    def handle_image_upload(self, request: ASGIRequest):
        form = OriginalImageForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(
                request=request,
                template_name="imageUpload.html",
                context={
                    "error": "Unknown file format",
                    # "image_exists": self.check_image_existence(),
                },
                status=200,
                content_type="text/html",
                using=None,
            )

        self.uploaded_original_image_file: InMemoryUploadedFile = request.FILES[
            "original_image_form"
        ]
        self.image: Image = open(self.uploaded_original_image_file)

        return

    @sync_to_async
    def check_image_constraints(self, request: ASGIRequest):
        if self.image.width > 2500 or self.image.height > 2500:
            context: dict = {
                "error": "Image dimensions should not be more than 2500x2500px",
                # "image_exists": self.check_image_existence(),
            }
            return render(request, "imageUpload.html", context)

        if self.uploaded_original_image_file.size > MAX_IMAGE_FILE_SIZE:
            context: dict = {
                "error": f"Image should not exceed {MAX_IMAGE_FILE_SIZE / 1_000_000} MB",
                # "image_exists": self.check_image_existence(),
            }
            return render(request, "imageUpload.html", context)

        return

    async def save_original_image(self, request: ASGIRequest):
        original_image = OriginalImage(
            image=ImageModel(
                user_id=self.user_id,
                image_name=self.new_image_name,
                content_type=self.uploaded_original_image_file.content_type,
                image_url=self.cloudinary_image_url,
                session_key=request.session.session_key,
                session_key_expiration_date=request.session.get_expiry_date(),
            )
        )

        await self.original_images_commands.create_original_image(original_image)

    @staticmethod
    @sync_to_async
    def get(request: ASGIRequest, *args, **kwargs):
        return render(
            request=request,
            template_name="imageUpload.html",
            context={
                "form": OriginalImageForm(),
                # "is_image_exist": await self.check_image_existence(),
            },
            status=200,
        )

    @async_csrf_protect_method
    async def post(self, request: ASGIRequest):
        await self.handle_user_session(request)
        self.original_images_commands = OriginalImagesCommands(self.user_id)

        await self.clean_up_previous_images()

        if "original_image_form" not in request.FILES:
            return render(
                request=request,
                template_name="imageUpload.html",
                context={
                    "error": "No image file was provided.",
                    # "is_image_exist": await self.check_image_existence(),
                },
            )

        response = await self.handle_image_upload(request)
        if isinstance(response, HttpResponse):
            return response

        constraints_response = await self.check_image_constraints(request)
        if isinstance(constraints_response, HttpResponse):
            return constraints_response

        self.uploaded_original_image_file.seek(0)

        await self.upload_original_image_to_cloudinary(
            self.uploaded_original_image_file
        )

        await self.save_original_image(request)
        self.image.close()

        await self.session_service.update_session()

        return redirect("ImageInfoView")
