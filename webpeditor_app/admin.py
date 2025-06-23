from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice

from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)
from webpeditor_app.models.editor import (
    EditorEditedImageAsset,
    EditorEditedImageAssetFile,
    EditorOriginalImageAsset,
    EditorOriginalImageAssetFile,
)
from webpeditor_app.views.admin_site import JazzminOTPAdminSite

# Admin site
admin_site: JazzminOTPAdminSite = JazzminOTPAdminSite(name="OTPAdmin")

# Auth Models
admin_site.register([User, Group, Session])  # pyright: ignore

# OTP Models
admin_site.register(TOTPDevice, TOTPDeviceAdmin)  # pyright: ignore


@admin.register(AppUser, site=admin_site)
class AppUserAdmin(admin.ModelAdmin[AppUser]):
    list_display = ("id", "session_key", "session_key_expiration_date")
    list_filter = ("session_key_expiration_date",)


@admin.register(ConverterImageAsset, site=admin_site)
class ConverterImageAssetAdmin(admin.ModelAdmin[ConverterImageAsset]):
    class OriginalImageAssetFileInline(admin.TabularInline[ConverterOriginalImageAssetFile, ConverterOriginalImageAssetFile]):
        model = ConverterOriginalImageAssetFile

    class ConvertedImageAssetFileInline(admin.TabularInline[ConverterConvertedImageAssetFile, ConverterConvertedImageAssetFile]):
        model = ConverterConvertedImageAssetFile

    list_display = ("id", "created_at", "user")
    list_filter = ("created_at", "user")
    date_hierarchy = "created_at"
    inlines = [OriginalImageAssetFileInline, ConvertedImageAssetFileInline]  # pyright: ignore [reportUnknownVariableType]


@admin.register(ConverterOriginalImageAssetFile, site=admin_site)
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


@admin.register(ConverterConvertedImageAssetFile, site=admin_site)
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


@admin.register(EditorOriginalImageAsset, site=admin_site)
class EditorOriginalImageAssetAdmin(admin.ModelAdmin[EditorOriginalImageAsset]):
    class EditorOriginalImageAssetFileInline(admin.TabularInline[EditorOriginalImageAssetFile, EditorOriginalImageAssetFile]):
        model = EditorOriginalImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user")
    list_filter = ("created_at", "user")
    date_hierarchy = "created_at"
    inlines = [EditorOriginalImageAssetFileInline]  # pyright: ignore [reportUnknownVariableType]


@admin.register(EditorOriginalImageAssetFile, site=admin_site)
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


@admin.register(EditorEditedImageAsset, site=admin_site)
class EditorEditedImageAssetAdmin(admin.ModelAdmin[EditorEditedImageAsset]):
    class EditorEditedImageAssetFileInline(admin.TabularInline[EditorEditedImageAssetFile, EditorEditedImageAssetFile]):
        model = EditorEditedImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user", "original_image_asset")
    list_filter = ("created_at", "user", "original_image_asset")
    date_hierarchy = "created_at"
    inlines = [EditorEditedImageAssetFileInline]  # pyright: ignore [reportUnknownVariableType]


@admin.register(EditorEditedImageAssetFile, site=admin_site)
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
