from django.db import models
from django.utils.translation import gettext_lazy as _

from infrastructure.database.models.base import BaseImageAssetDo, BaseImageAssetFileDo


# TODO: Merge into one EditorImageAsset that will contain 2 asset files - EditorOriginalImageAssetFile and EditorEditedImageAssetFile
class EditorOriginalImageAssetDo(BaseImageAssetDo):
    class Meta(BaseImageAssetDo.Meta):
        verbose_name: str = _("Editor Original Image Asset")
        verbose_name_plural: str = _("Editor Original Image Assets")


class EditorOriginalImageAssetFileDo(BaseImageAssetFileDo):
    original_image_asset: models.OneToOneField[EditorOriginalImageAssetDo] = models.OneToOneField(
        EditorOriginalImageAssetDo,
        related_name="original_image_asset_file",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFileDo.Meta):
        verbose_name: str = _("Editor Original Image Asset File")
        verbose_name_plural: str = _("Editor Original Image Asset Files")


class EditorEditedImageAssetDo(BaseImageAssetDo):
    original_image_asset: models.OneToOneField[EditorOriginalImageAssetDo] = models.OneToOneField(
        EditorOriginalImageAssetDo,
        related_name="edited_image_asset",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetDo.Meta):
        verbose_name: str = _("Editor Edited Image Asset")
        verbose_name_plural: str = _("Editor Edited Image Assets")


class EditorEditedImageAssetFileDo(BaseImageAssetFileDo):
    edited_image_asset: models.OneToOneField[EditorEditedImageAssetDo] = models.OneToOneField(
        EditorEditedImageAssetDo,
        related_name="edited_image_asset_file",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFileDo.Meta):
        verbose_name: str = _("Editor Edited Image Asset File")
        verbose_name_plural: str = _("Editor Edited Image Asset Files")
