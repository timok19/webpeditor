from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import URLPattern, path
from django.utils.html import format_html
from django.utils.safestring import SafeText

from webpeditor_app.common import api_key_utils
from webpeditor_app.globals import Pair
from webpeditor_app.infrastructure.database.models import (
    APIKey,
    AppUser,
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
    EditorEditedImageAsset,
    EditorEditedImageAssetFile,
    EditorOriginalImageAsset,
    EditorOriginalImageAssetFile,
)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin[APIKey]):
    list_display = ("email", "key_hash", "created_at", "generate_new_key_button")
    list_filter = ("email", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("key_hash", "created_at")

    def get_urls(self) -> list[URLPattern]:
        generate_api_key_url = path(
            "generate-key/<int:api_key_id>/",
            self.admin_site.admin_view(self.generate_new_key_view),
            name="generate-api-key",
        )
        return [generate_api_key_url] + super().get_urls()

    def save_model(self, request: HttpRequest, obj: APIKey, form: ModelForm, change: bool) -> None:
        if change:
            super().save_model(request, obj, form, change)
        else:
            api_key, key_hash = self.__create_api_key_and_hash()
            obj.key_hash = key_hash
            super().save_model(request, obj, form, change)
            self.__notify_api_key_created(request, obj.email, api_key)

    def generate_new_key_view(self, request: HttpRequest, api_key_id: int):
        api_key, key_hash = self.__create_api_key_and_hash()

        api_key_obj = APIKey.objects.get(pk=api_key_id)
        api_key_obj.key_hash = key_hash
        api_key_obj.save()

        self.__notify_api_key_created(request, api_key_obj.email, api_key)

        return redirect("admin:webpeditor_app_apikey_changelist")

    @staticmethod
    def generate_new_key_button(obj: APIKey) -> SafeText:
        return format_html('<a class="button" href="/admin/webpeditor_app/apikey/generate-key/{}/">Generate New Key</a>', obj.pk)

    @staticmethod
    def __create_api_key_and_hash() -> Pair[str, str]:
        api_key = api_key_utils.create_api_key()
        api_key_hash = api_key_utils.create_api_key_hash(api_key)
        return Pair[str, str](api_key, api_key_hash)

    @staticmethod
    def __notify_api_key_created(request: HttpRequest, email: str, api_key: str) -> None:
        messages.success(request, f'New API key generated for "{email}": {api_key} (Save this key, it won\'t be shown again)')


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin[AppUser]):
    list_display = ("id", "session_key", "session_key_expiration_date")
    list_filter = ("session_key_expiration_date",)


@admin.register(ConverterImageAsset)
class ConverterImageAssetAdmin(admin.ModelAdmin[ConverterImageAsset]):
    class OriginalImageAssetFileInline(admin.TabularInline[ConverterOriginalImageAssetFile]):
        model = ConverterOriginalImageAssetFile

    class ConvertedImageAssetFileInline(admin.TabularInline[ConverterConvertedImageAssetFile]):
        model = ConverterConvertedImageAssetFile

    list_display = ("id", "created_at", "user")
    list_filter = ("created_at", "user")
    date_hierarchy = "created_at"
    inlines = [OriginalImageAssetFileInline, ConvertedImageAssetFileInline]


@admin.register(ConverterOriginalImageAssetFile)
class ConverterOriginalImageAssetFileAdmin(admin.ModelAdmin[ConverterOriginalImageAssetFile]):
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


@admin.register(ConverterConvertedImageAssetFile)
class ConverterConvertedImageAssetFileAdmin(admin.ModelAdmin[ConverterConvertedImageAssetFile]):
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


@admin.register(EditorOriginalImageAsset)
class EditorOriginalImageAssetAdmin(admin.ModelAdmin[EditorOriginalImageAsset]):
    class EditorOriginalImageAssetFileInline(admin.TabularInline[EditorOriginalImageAssetFile]):
        model = EditorOriginalImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user")
    list_filter = ("created_at", "user")
    date_hierarchy = "created_at"
    inlines = [EditorOriginalImageAssetFileInline]


@admin.register(EditorOriginalImageAssetFile)
class EditorOriginalImageAssetFileAdmin(admin.ModelAdmin[EditorOriginalImageAssetFile]):
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


@admin.register(EditorEditedImageAsset)
class EditorEditedImageAssetAdmin(admin.ModelAdmin[EditorEditedImageAsset]):
    class EditorEditedImageAssetFileInline(admin.TabularInline[EditorEditedImageAssetFile]):
        model = EditorEditedImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user", "original_image_asset")
    list_filter = ("created_at", "user", "original_image_asset")
    date_hierarchy = "created_at"
    inlines = [EditorEditedImageAssetFileInline]


@admin.register(EditorEditedImageAssetFile)
class EditorEditedImageAssetFileAdmin(admin.ModelAdmin[EditorEditedImageAssetFile]):
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
