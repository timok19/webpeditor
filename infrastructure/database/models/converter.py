from django.db import models
from django.utils.translation import gettext_lazy as _

from infrastructure.database.models.base import BaseImageAssetDo, BaseImageAssetFileDo


class ConverterImageAssetDo(BaseImageAssetDo):
    class Meta(BaseImageAssetDo.Meta):
        verbose_name: str = _("Converter Image Asset")
        verbose_name_plural: str = _("Converter Image Assets")


class ConverterOriginalImageAssetFileDo(BaseImageAssetFileDo):
    image_asset: models.ForeignKey[ConverterImageAssetDo] = models.ForeignKey(
        ConverterImageAssetDo,
        related_name="original_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFileDo.Meta):
        verbose_name: str = _("Converter Original Image Asset File")
        verbose_name_plural: str = _("Converter Original Image Asset Files")


class ConverterConvertedImageAssetFileDo(BaseImageAssetFileDo):
    image_asset: models.ForeignKey[ConverterImageAssetDo] = models.ForeignKey(
        ConverterImageAssetDo,
        related_name="converted_image_asset_files",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFileDo.Meta):
        verbose_name: str = _("Converter Converted Image Asset File")
        verbose_name_plural: str = _("Converter Converted Image Asset Files")
