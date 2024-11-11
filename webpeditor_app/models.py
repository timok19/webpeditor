from django.db import models
from django.utils import timezone


def upload_to_folder(instance: object, filename: str) -> str:
    if isinstance(instance, ConvertedImageAssetFile):
        return f"{instance.converted_image_asset.user_id}/converted/{filename}"

    if isinstance(instance, EditedImageAssetFile):
        return f"{instance.edited_image_asset.user_id}/edited/{filename}"

    if isinstance(instance, OriginalImageAssetFile):
        return f"{instance.original_image_asset.user_id}/{filename}"

    return filename


class BaseImageAsset(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=32, null=True)
    session_key = models.CharField(max_length=120, null=True)
    session_key_expiration_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.id)


##################################################### ORIGINAL IMAGES #############################################
class OriginalImageAsset(BaseImageAsset):
    image_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)

    class Meta(BaseImageAsset.Meta):
        verbose_name = "Original Image Asset"
        verbose_name_plural = "Original Image Assets"


class OriginalImageAssetFile(models.Model):
    id = models.AutoField(primary_key=True)
    image_file = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)

    original_image_asset = models.OneToOneField(OriginalImageAsset, related_name="image_file", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Original Image Asset File"
        verbose_name_plural = "Original Image Asset Files"

    def __str__(self) -> str:
        return str(self.id)


##################################################### EDITED IMAGES #############################################
class EditedImageAsset(BaseImageAsset):
    image_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=255)

    original_image_asset = models.OneToOneField(OriginalImageAsset, related_name="edited_image_asset", on_delete=models.CASCADE)

    class Meta(BaseImageAsset.Meta):
        verbose_name = "Edited Image Asset"
        verbose_name_plural = "Edited Image Assets"


class EditedImageAssetFile(models.Model):
    id = models.AutoField(primary_key=True)
    image_file = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)

    edited_image_asset = models.OneToOneField(EditedImageAsset, related_name="image_file", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Edited Image Asset File"
        verbose_name_plural = "Edited Image Asset Files"

    def __str__(self) -> str:
        return str(self.id)


##################################################### CONVERTED IMAGES #############################################
class ConvertedImageAsset(BaseImageAsset):
    class Meta(BaseImageAsset.Meta):
        verbose_name = "Converted Image Asset"
        verbose_name_plural = "Converted Image Assets"


class ConvertedImageAssetFile(models.Model):
    id = models.AutoField(primary_key=True)
    image_file = models.ImageField(upload_to=upload_to_folder, blank=True, max_length=1024)

    converted_image_asset = models.ForeignKey(ConvertedImageAsset, related_name="image_files", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Converted Image Asset File"
        verbose_name_plural = "Converted Image Asset Files"

    def __str__(self) -> str:
        return str(self.id)
