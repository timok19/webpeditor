from django.db import models
from django.utils.translation import gettext_lazy as _

from webpeditor_app.models.base import BaseImageAsset, BaseImageAssetFile
from webpeditor_app.models.app_user import AppUser


def upload_to_folder(instance: object, filename: str) -> str:
    if isinstance(instance, ConverterOriginalImageAssetFile):
        return f"{instance.image_asset.user.id}/converter/original/{filename}"
    elif isinstance(instance, ConverterConvertedImageAssetFile):
        return f"{instance.image_asset.user.id}/converter/converted/{filename}"
    else:
        raise ValueError("%r is not a recognized image asset file type", instance)


class ConverterImageAsset(BaseImageAsset):
    user = models.OneToOneField(AppUser, related_name="user_converted_image_asset", on_delete=models.DO_NOTHING)

    class Meta(BaseImageAsset.Meta):
        verbose_name: str = _("Converted Image Asset")
        verbose_name_plural: str = _("Converted Image Assets")


class ConverterOriginalImageAssetFile(BaseImageAssetFile):
    file: models.ImageField = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)
    image_asset: models.ForeignKey[ConverterImageAsset] = models.ForeignKey(
        ConverterImageAsset,
        related_name="original_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = _("Original Image Asset File")
        verbose_name_plural: str = _("Original Image Asset Files")


class ConverterConvertedImageAssetFile(BaseImageAssetFile):
    file: models.ImageField = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)
    image_asset: models.ForeignKey[ConverterImageAsset] = models.ForeignKey(
        ConverterImageAsset, related_name="converted_image_asset_files", on_delete=models.CASCADE
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = _("Converted Image Asset File")
        verbose_name_plural: str = _("Converted Image Asset Files")
