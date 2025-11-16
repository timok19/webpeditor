from django.db import models
from django.utils.translation import gettext_lazy as _

from common.infrastructure.database.models import BaseImageAsset, BaseImageAssetFile


# TODO: Merge into one EditorImageAsset that will contain 2 asset files - EditorOriginalImageAssetFile and EditorEditedImageAssetFile
class EditorOriginalImageAsset(BaseImageAsset):
    class Meta(BaseImageAsset.Meta):
        verbose_name: str = _("Editor Original Image Asset")
        verbose_name_plural: str = _("Editor Original Image Assets")


class EditorOriginalImageAssetFile(BaseImageAssetFile):
    original_image_asset: models.OneToOneField[EditorOriginalImageAsset] = models.OneToOneField(
        EditorOriginalImageAsset,
        related_name="original_image_asset_file",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = _("Editor Original Image Asset File")
        verbose_name_plural: str = _("Editor Original Image Asset Files")


class EditorEditedImageAsset(BaseImageAsset):
    original_image_asset: models.OneToOneField[EditorOriginalImageAsset] = models.OneToOneField(
        EditorOriginalImageAsset,
        related_name="edited_image_asset",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAsset.Meta):
        verbose_name: str = _("Editor Edited Image Asset")
        verbose_name_plural: str = _("Editor Edited Image Assets")


class EditorEditedImageAssetFile(BaseImageAssetFile):
    edited_image_asset: models.OneToOneField[EditorEditedImageAsset] = models.OneToOneField(
        EditorEditedImageAsset,
        related_name="edited_image_asset_file",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = _("Editor Edited Image Asset File")
        verbose_name_plural: str = _("Editor Edited Image Asset Files")
