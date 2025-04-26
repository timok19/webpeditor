from django.db import models
from django.utils.translation import gettext_lazy as _

from webpeditor_app.models.base import BaseImageAsset, BaseImageAssetFile
from webpeditor_app.models.app_user import AppUser


def upload_to_folder(instance: object, filename: str) -> str:
    if isinstance(instance, EditorOriginalImageAssetFile):
        return f"{instance.original_image_asset.user.id}/editor/original/{filename}"
    elif isinstance(instance, EditorEditedImageAssetFile):
        return f"{instance.edited_image_asset.user.id}/editor/edited/{filename}"
    else:
        raise ValueError(f"{instance!r} is not a recognized image asset file type")


class EditorOriginalImageAsset(BaseImageAsset):
    user: models.OneToOneField[AppUser, AppUser] = models.OneToOneField(
        AppUser,
        related_name="user_original_image_asset",
        on_delete=models.DO_NOTHING,
    )

    class Meta(BaseImageAsset.Meta):
        verbose_name: str = str(_("Original Image Asset"))
        verbose_name_plural: str = str(_("Original Image Assets"))


class EditorOriginalImageAssetFile(BaseImageAssetFile):
    image_file: models.ImageField = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)
    original_image_asset: models.OneToOneField[EditorOriginalImageAsset, EditorOriginalImageAsset] = (
        models.OneToOneField(
            EditorOriginalImageAsset,
            related_name="original_image_asset_file",
            on_delete=models.CASCADE,
        )
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = str(_("Original Image Asset File"))
        verbose_name_plural: str = str(_("Original Image Asset Files"))


class EditorEditedImageAsset(BaseImageAsset):
    user: models.OneToOneField[AppUser, AppUser] = models.OneToOneField(
        AppUser,
        related_name="user_edited_image_asset",
        on_delete=models.DO_NOTHING,
    )
    original_image_asset: models.OneToOneField[EditorOriginalImageAsset, EditorOriginalImageAsset] = (
        models.OneToOneField(
            EditorOriginalImageAsset,
            related_name="edited_image_asset",
            on_delete=models.CASCADE,
        )
    )

    class Meta(BaseImageAsset.Meta):
        verbose_name: str = str(_("Edited Image Asset"))
        verbose_name_plural: str = str(_("Edited Image Assets"))


class EditorEditedImageAssetFile(BaseImageAssetFile):
    file: models.ImageField = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)
    edited_image_asset: models.OneToOneField[EditorEditedImageAsset, EditorEditedImageAsset] = models.OneToOneField(
        EditorEditedImageAsset,
        related_name="edited_image_asset_file",
        on_delete=models.CASCADE,
    )

    class Meta(BaseImageAssetFile.Meta):
        verbose_name: str = str(_("Edited Image Asset File"))
        verbose_name_plural: str = str(_("Edited Image Asset Files"))
