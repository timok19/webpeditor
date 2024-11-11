from typing import Any
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from webpeditor_app.models import OriginalImageAsset, EditedImageAsset, ConvertedImageAsset, ConvertedImageAssetFile


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImageAsset
        fields = (
            "id",
            "image_name",
            "content_type",
            "image_url",
            "user_id",
            "session_key",
            "session_key_expiration_date",
            "created_at",
        )


class EditedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditedImageAsset
        fields = (
            "id",
            "original_image_asset",
            "image_name",
            "content_type",
            "image_url",
            "user_id",
            "session_key",
            "session_key_expiration_date",
            "created_at",
        )


class ConvertedImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConvertedImageAssetFile
        fields = ("id", "image_file")


class ConvertedImageSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=True)

    class Meta:
        model = ConvertedImageAsset
        fields = (
            "id",
            "user_id",
            "image_files",
            "session_key",
            "session_key_expiration_date",
            "created_at",
        )

    def create(self, validated_data: dict[str, Any]) -> ConvertedImageAsset:
        # Extract image files from the validated data
        image_files: list[Any] = validated_data.pop("image_files", [])
        converted_image_asset: ConvertedImageAsset = ConvertedImageAsset.objects.create(**validated_data)

        # Use bulk_create to insert all image files at once
        ConvertedImageAssetFile.objects.bulk_create(
            [
                ConvertedImageAssetFile(
                    converted_image_asset=converted_image_asset,
                    image_file=file,
                )
                for file in image_files
            ]
        )

        return converted_image_asset

    def update(self, instance: ConvertedImageAsset, validated_data: dict[str, Any]) -> ConvertedImageAsset:
        # Extract image files from the validated data
        image_files: list[UploadedFile] = validated_data.pop("image_files", [])

        # Update the fields of ConvertedImage
        instance.user_id = validated_data.get("user_id", instance.user_id)
        instance.session_key = validated_data.get("session_key", instance.session_key)
        instance.created_at = validated_data.get("created_at", instance.created_at)
        instance.session_key_expiration_date = validated_data.get("session_key_expiration_date", instance.session_key_expiration_date)
        instance.save()

        if len(image_files) > 0:
            instance.image_files.all().delete()  # pyright: ignore [reportAttributeAccessIssue]

            ConvertedImageAssetFile.objects.bulk_create(
                [
                    ConvertedImageAssetFile(
                        converted_image_asset=instance,
                        image_file=file,
                    )
                    for file in image_files
                ]
            )

        return instance

    def to_representation(self, instance: ConvertedImageAsset) -> dict[str, Any]:
        representation: dict[str, Any] = super().to_representation(instance)
        representation["image_files"] = [file.image_file.url for file in instance.image_files.all()]  # pyright: ignore [reportAttributeAccessIssue]
        return representation
