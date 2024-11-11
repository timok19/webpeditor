from django.contrib import admin
from django.contrib.auth.models import Group, User
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice

from webpeditor.views import JazzminOTPAdminSite
from webpeditor_app.models import (
    OriginalImageAsset,
    EditedImageAsset,
    ConvertedImageAsset,
    ConvertedImageAssetFile,
    OriginalImageAssetFile,
    EditedImageAssetFile,
)


##################################################### ORIGINAL IMAGES #############################################
class OriginalImageAssetFileInline(admin.TabularInline):
    model = OriginalImageAssetFile
    extra = 1


class OriginalImageAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_name",
        "content_type",
        "user_id",
        "session_key",
        "session_key_expiration_date",
        "created_at",
    )
    list_filter = ("session_key_expiration_date", "created_at")
    date_hierarchy = "created_at"
    inlines = [OriginalImageAssetFileInline]


class OriginalImageAssetFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_file",
        "original_image_asset",
    )
    list_filter = (
        "original_image_asset",
        "original_image_asset__session_key_expiration_date",
        "original_image_asset__created_at",
    )
    date_hierarchy = "original_image_asset__created_at"


##################################################### EDITED IMAGES #############################################
class EditedImageAssetFileInline(admin.TabularInline):
    model = EditedImageAssetFile
    extra = 1


class EditedImageAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "original_image_asset",
        "image_name",
        "content_type",
        "user_id",
        "session_key",
        "session_key_expiration_date",
        "created_at",
    )
    list_filter = (
        "original_image_asset",
        "session_key_expiration_date",
        "created_at",
    )
    date_hierarchy = "created_at"
    inlines = [EditedImageAssetFileInline]


class EditedImageAssetFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_file",
        "edited_image_asset",
    )
    list_filter = (
        "edited_image_asset",
        "edited_image_asset__session_key_expiration_date",
        "edited_image_asset__created_at",
    )
    date_hierarchy = "edited_image_asset__created_at"


##################################################### CONVERTED IMAGES #############################################
class ConvertedImageAssetFileInline(admin.TabularInline):
    model = ConvertedImageAssetFile


class ConvertedImageAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "session_key",
        "session_key_expiration_date",
        "created_at",
    )
    list_filter = ("session_key_expiration_date", "created_at")
    date_hierarchy = "created_at"
    inlines = [ConvertedImageAssetFileInline]


class ConvertedImageAssetFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_file",
        "converted_image_asset",
    )
    list_filter = (
        "converted_image_asset",
        "converted_image_asset__session_key_expiration_date",
        "converted_image_asset__created_at",
    )
    date_hierarchy = "converted_image_asset__created_at"


class JazzminOTPAdmin(JazzminOTPAdminSite): ...


admin_site: JazzminOTPAdmin = JazzminOTPAdmin(name="OTPAdmin")

# Auth Models
admin_site.register(User)
admin_site.register(Group)

# OTP Models
admin_site.register(TOTPDevice, TOTPDeviceAdmin)

# WebP Editor Models
admin_site.register(OriginalImageAsset, OriginalImageAssetAdmin)
admin_site.register(OriginalImageAssetFile, OriginalImageAssetFileAdmin)
admin_site.register(EditedImageAsset, EditedImageAssetAdmin)
admin_site.register(EditedImageAssetFile, EditedImageAssetFileAdmin)
admin_site.register(ConvertedImageAsset, ConvertedImageAssetAdmin)
admin_site.register(ConvertedImageAssetFile, ConvertedImageAssetFileAdmin)
