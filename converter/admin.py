from django.contrib import admin

from converter.infrastructure.database.models import (
    ConverterConvertedImageAssetFile,
    ConverterImageAsset,
    ConverterOriginalImageAssetFile,
)


@admin.register(ConverterImageAsset)
class ConverterImageAssetAdmin(admin.ModelAdmin[ConverterImageAsset]):
    class OriginalImageAssetFileInline(admin.TabularInline[ConverterOriginalImageAssetFile]):
        model = ConverterOriginalImageAssetFile

    class ConvertedImageAssetFileInline(admin.TabularInline[ConverterConvertedImageAssetFile]):
        model = ConverterConvertedImageAssetFile

    list_display = ("id", "created_at", "user_id")
    list_filter = ("created_at", "user_id")
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
