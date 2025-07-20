from django.contrib import admin

from webpeditor_app.infrastructure.database.models import AppUser
from webpeditor_app.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)
from webpeditor_app.infrastructure.database.models import (
    EditorEditedImageAsset,
    EditorEditedImageAssetFile,
    EditorOriginalImageAsset,
    EditorOriginalImageAssetFile,
)


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
    inlines = [OriginalImageAssetFileInline, ConvertedImageAssetFileInline]  # pyright: ignore [reportUnknownVariableType]


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
    inlines = [EditorOriginalImageAssetFileInline]  # pyright: ignore [reportUnknownVariableType]


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
    inlines = [EditorEditedImageAssetFileInline]  # pyright: ignore [reportUnknownVariableType]


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
