from django.contrib import admin

from editor.infrastructure.database.models import (
    EditorEditedImageAsset,
    EditorEditedImageAssetFile,
    EditorOriginalImageAsset,
    EditorOriginalImageAssetFile,
)


@admin.register(EditorOriginalImageAsset)
class EditorOriginalImageAssetAdmin(admin.ModelAdmin[EditorOriginalImageAsset]):
    class EditorOriginalImageAssetFileInline(admin.TabularInline[EditorOriginalImageAssetFile]):
        model = EditorOriginalImageAssetFile
        extra = 1

    list_display = ("id", "created_at", "user_id")
    list_filter = ("created_at", "user_id")
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

    list_display = ("id", "created_at", "user_id", "original_image_asset")
    list_filter = ("created_at", "user_id", "original_image_asset")
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
