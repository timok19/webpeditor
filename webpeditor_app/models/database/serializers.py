from rest_framework import serializers

from webpeditor_app.models.database.models import (
    OriginalImage,
    EditedImage,
    ConvertedImage,
)


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = (
            "image_id",
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
        model = EditedImage
        fields = (
            "image_id",
            "original_image",
            "image_name",
            "content_type",
            "image_url",
            "user_id",
            "session_key",
            "session_key_expiration_date",
            "created_at",
        )


class ConvertedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConvertedImage
        fields = (
            "user_id",
            "image_set",
            "session_key",
            "session_key_expiration_date",
            "created_at",
        )
