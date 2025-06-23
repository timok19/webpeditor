from django.db import models
from django.utils.translation import gettext_lazy as _

from webpeditor_app.models.app_user import AppUser
from webpeditor_app.models.base import BaseImageAsset, BaseImageAssetFile


class ConverterImageAsset(BaseImageAsset):
    user: models.OneToOneField[AppUser, AppUser] = models.OneToOneField(
        AppUser,
        related_name="user_converted_image_asset",
        on_delete=models.DO_NOTHING,
    )

    class Meta(BaseImageAsset.Meta):
        verbose_name: str = str(_("Converted Image Asset"))
        verbose_name_plural: str = str(_("Converted Image Assets"))


class ConverterOriginalImageAssetFile(BaseImageAssetFile):
    image_asset: models.ForeignKey[ConverterImageAsset, ConverterImageAsset] = models.ForeignKey(
        ConverterImageAsset,
        related_name="original_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = str(_("Original Image Asset File"))
        verbose_name_plural: str = str(_("Original Image Asset Files"))


class ConverterConvertedImageAssetFile(BaseImageAssetFile):
    image_asset: models.ForeignKey[ConverterImageAsset, ConverterImageAsset] = models.ForeignKey(
        ConverterImageAsset,
        related_name="converted_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = str(_("Converted Image Asset File"))
        verbose_name_plural: str = str(_("Converted Image Asset Files"))
