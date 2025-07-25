from django.db import models
from django.utils.translation import gettext_lazy as _

from webpeditor_app.infrastructure.database.models.app_user import AppUser
from webpeditor_app.infrastructure.database.models.base import BaseImageAsset, BaseImageAssetFile


class ConverterImageAsset(BaseImageAsset):
    user: models.OneToOneField[AppUser] = models.OneToOneField(
        AppUser,
        related_name="user_converted_image_asset",
        on_delete=models.DO_NOTHING,
    )

    class Meta(BaseImageAsset.Meta):
        verbose_name: str = _("Converter Image Asset")
        verbose_name_plural: str = _("Converter Image Assets")


class ConverterOriginalImageAssetFile(BaseImageAssetFile):
    image_asset: models.ForeignKey[ConverterImageAsset] = models.ForeignKey(
        ConverterImageAsset,
        related_name="original_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = _("Converter Original Image Asset File")
        verbose_name_plural: str = _("Converter Original Image Asset Files")


class ConverterConvertedImageAssetFile(BaseImageAssetFile):
    image_asset: models.ForeignKey[ConverterImageAsset] = models.ForeignKey(
        ConverterImageAsset,
        related_name="converted_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = _("Converter Converted Image Asset File")
        verbose_name_plural: str = _("Converter Converted Image Asset Files")
