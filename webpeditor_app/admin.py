from django.contrib import admin
from django.contrib.auth.models import User, Group
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice

from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.converter import (
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
    ConverterConvertedImageAssetFile,
)
from webpeditor_app.models.editor import (
    EditorOriginalImageAsset,
    EditorOriginalImageAssetFile,
    EditorEditedImageAsset,
    EditorEditedImageAssetFile,
)
from webpeditor_app.views.admin_site import JazzminOTPAdminSite

# Admin site
admin_site: JazzminOTPAdminSite = JazzminOTPAdminSite(name="OTPAdmin")

# Auth Models
admin_site.register([User, Group])

# OTP Models
admin_site.register(TOTPDevice, TOTPDeviceAdmin)


@admin.register(AppUser, site=admin_site)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ("id", "session_key", "session_key_expiration_date")
    list_filter = ("session_key_expiration_date",)


@admin.register(ConverterImageAsset, site=admin_site)
class ConverterImageAssetAdmin(admin.ModelAdmin):
    class OriginalImageAssetFileInline(admin.TabularInline):
        model = ConverterOriginalImageAssetFile

    class ConvertedImageAssetFileInline(admin.TabularInline):
        model = ConverterConvertedImageAssetFile

    list_display = ("id", "created_at", "user")
    list_filter = ("created_at", "user")
    date_hierarchy = "created_at"
    inlines = [OriginalImageAssetFileInline, ConvertedImageAssetFileInline]


@admin.register(ConverterOriginalImageAssetFile, site=admin_site)
class ConverterOriginalImageAssetFileAdmin(admin.ModelAdmin):
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
        "file",
        "image_asset",
    )
    list_filter = ("image_asset",)


@admin.register(ConverterConvertedImageAssetFile, site=admin_site)
class ConverterConvertedImageAssetFileAdmin(admin.ModelAdmin):
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
        "file",
        "image_asset",
    )
    list_filter = ("image_asset",)


@admin.register(EditorOriginalImageAsset, site=admin_site)
class EditorOriginalImageAssetAdmin(admin.ModelAdmin):
    class EditorOriginalImageAssetFileInline(admin.TabularInline):
        model = EditorOriginalImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user")
    list_filter = ("created_at", "user")
    date_hierarchy = "created_at"
    inlines = [EditorOriginalImageAssetFileInline]


@admin.register(EditorOriginalImageAssetFile, site=admin_site)
class EditorOriginalImageAssetFileAdmin(admin.ModelAdmin):
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
        "image_file",
        "original_image_asset",
    )
    list_filter = ("original_image_asset",)


@admin.register(EditorEditedImageAsset, site=admin_site)
class EditorEditedImageAssetAdmin(admin.ModelAdmin):
    class EditorEditedImageAssetFileInline(admin.TabularInline):
        model = EditorEditedImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user", "original_image_asset")
    list_filter = ("created_at", "user", "original_image_asset")
    date_hierarchy = "created_at"
    inlines = [EditorEditedImageAssetFileInline]


@admin.register(EditorEditedImageAssetFile, site=admin_site)
class EditorEditedImageAssetFileAdmin(admin.ModelAdmin):
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
        "file",
        "edited_image_asset",
    )
    list_filter = ("edited_image_asset",)
