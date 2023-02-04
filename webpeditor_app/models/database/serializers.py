from rest_framework import serializers
from webpeditor_app.models.database.models import OriginalImage, EditedImage


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = ('image_id',
                  'file_name',
                  'content_type',
                  'original_image_url',
                  'session_id',
                  'created_at',
                  'updated_at'
                  )


class EditedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditedImage
        fields = ('edited_image_id',
                  'original_image',
                  'content_type_edited',
                  'edited_image_url',
                  'session_id',
                  'created_at',
                  'updated_at'
                  )
