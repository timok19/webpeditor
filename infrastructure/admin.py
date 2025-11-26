from typing import Union

from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import URLPattern, path
from django.utils.html import format_html
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _

from infrastructure.database.models.api import APIKey
from infrastructure.utils import APIKeyUtils
from core.types import Pair
from infrastructure.database.models.converter import (
    ConverterConvertedImageAssetFileDo,
    ConverterImageAssetDo,
    ConverterOriginalImageAssetFileDo,
)
from infrastructure.database.models.editor import (
    EditorEditedImageAssetDo,
    EditorEditedImageAssetFileDo,
    EditorOriginalImageAssetDo,
    EditorOriginalImageAssetFileDo,
)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin[APIKey]):
    list_display = ("email", "key_hash", "created_at", "generate_new_key")
    list_filter = ("email", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("key_hash", "created_at")

    def get_urls(self) -> list[URLPattern]:
        view = self.admin_site.admin_view(self.generate_new_key_view)
        return [path("generate-key/<int:api_key_id>/", view, name="generate-api-key")] + super().get_urls()

    def save_model(self, request: HttpRequest, obj: APIKey, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
            return None

        api_key, key_hash = self.__create_api_key_and_hash()
        obj.key_hash = key_hash
        super().save_model(request, obj, form, change)
        self.__notify_api_key_created(request, obj.email, api_key)
        return None

    def generate_new_key_view(self, request: HttpRequest, api_key_id: int) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        api_key, key_hash = self.__create_api_key_and_hash()
        api_key_obj = APIKey.objects.get(pk=api_key_id)
        api_key_obj.key_hash = key_hash
        api_key_obj.save()
        self.__notify_api_key_created(request, api_key_obj.email, api_key)
        return redirect("admin:webpeditor_app_apikey_changelist")

    @staticmethod
    def generate_new_key(obj: APIKey) -> SafeText:
        return format_html('<a class="button" href="/admin/webpeditor_app/apikey/generate-key/{}/">{}</a>', obj.pk, _("Generate New Key"))

    @staticmethod
    def __create_api_key_and_hash() -> Pair[str, str]:
        api_key = APIKeyUtils.create()
        api_key_hash = APIKeyUtils.hash(api_key)
        return Pair[str, str](api_key, api_key_hash)

    @staticmethod
    def __notify_api_key_created(request: HttpRequest, email: str, api_key: str) -> None:
        message = _("New API key generated for") + f' "{email}": {api_key} ' + _("(Save this key, it won't be shown again)")
        messages.success(request, message)
        return None


@admin.register(ConverterImageAssetDo)
class ConverterImageAssetAdmin(admin.ModelAdmin[ConverterImageAssetDo]):
    class OriginalImageAssetFileInline(admin.TabularInline[ConverterOriginalImageAssetFileDo]):
        model = ConverterOriginalImageAssetFileDo

    class ConvertedImageAssetFileInline(admin.TabularInline[ConverterConvertedImageAssetFileDo]):
        model = ConverterConvertedImageAssetFileDo

    list_display = ("id", "created_at", "user_id")
    list_filter = ("created_at", "user_id")
    date_hierarchy = "created_at"
    inlines = [OriginalImageAssetFileInline, ConvertedImageAssetFileInline]


@admin.register(ConverterOriginalImageAssetFileDo)
class ConverterOriginalImageAssetFileAdmin(admin.ModelAdmin[ConverterOriginalImageAssetFileDo]):
    list_display = (
        "id",
        "filename",
        "filename_shorter",
        "content_type",
        "format",
        "format_description",
        "size",
        "width",
        "height",
        "aspect_ratio",
        "color_mode",
        "exif_data",
        "file_url",
        "image_asset",
    )
    list_filter = ("image_asset",)


@admin.register(ConverterConvertedImageAssetFileDo)
class ConverterConvertedImageAssetFileAdmin(admin.ModelAdmin[ConverterConvertedImageAssetFileDo]):
    list_display = (
        "id",
        "filename",
        "filename_shorter",
        "content_type",
        "format",
        "format_description",
        "size",
        "width",
        "height",
        "aspect_ratio",
        "color_mode",
        "exif_data",
        "file_url",
        "image_asset",
    )
    list_filter = ("image_asset",)


@admin.register(EditorOriginalImageAssetDo)
class EditorOriginalImageAssetAdmin(admin.ModelAdmin[EditorOriginalImageAssetDo]):
    class EditorOriginalImageAssetFileInline(admin.TabularInline[EditorOriginalImageAssetFileDo]):
        model = EditorOriginalImageAssetFileDo
        extra = 1

    list_display = ("id", "created_at", "user_id")
    list_filter = ("created_at", "user_id")
    date_hierarchy = "created_at"
    inlines = [EditorOriginalImageAssetFileInline]


@admin.register(EditorOriginalImageAssetFileDo)
class EditorOriginalImageAssetFileAdmin(admin.ModelAdmin[EditorOriginalImageAssetFileDo]):
    list_display = (
        "id",
        "filename",
        "filename_shorter",
        "content_type",
        "format",
        "format_description",
        "size",
        "width",
        "height",
        "aspect_ratio",
        "color_mode",
        "exif_data",
        "file_url",
        "original_image_asset",
    )
    list_filter = ("original_image_asset",)


@admin.register(EditorEditedImageAssetDo)
class EditorEditedImageAssetAdmin(admin.ModelAdmin[EditorEditedImageAssetDo]):
    class EditorEditedImageAssetFileInline(admin.TabularInline[EditorEditedImageAssetFileDo]):
        model = EditorEditedImageAssetFileDo
        extra = 1

    list_display = ("id", "created_at", "user_id", "original_image_asset")
    list_filter = ("created_at", "user_id", "original_image_asset")
    date_hierarchy = "created_at"
    inlines = [EditorEditedImageAssetFileInline]


@admin.register(EditorEditedImageAssetFileDo)
class EditorEditedImageAssetFileAdmin(admin.ModelAdmin[EditorEditedImageAssetFileDo]):
    list_display = (
        "id",
        "filename",
        "filename_shorter",
        "content_type",
        "format",
        "format_description",
        "size",
        "width",
        "height",
        "aspect_ratio",
        "color_mode",
        "exif_data",
        "file_url",
        "edited_image_asset",
    )
    list_filter = ("edited_image_asset",)
