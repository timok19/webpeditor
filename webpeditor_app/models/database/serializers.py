from rest_framework import serializers

from webpeditor_app.models.database.models import OriginalImage, EditedImage


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = (
            'image_id',
            'image_name',
            'content_type',
            'original_image',
            'user_id',
            'session_id',
            'session_id_expiration_date',
            'created_at',
        )


class EditedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditedImage
        fields = (
            'edited_image_id',
            'original_image',
            'edited_image_name',
            'content_type_edited',
            'edited_image',
            'user_id',
            'session_id',
            'session_id_expiration_date',
            'created_at',
        )
