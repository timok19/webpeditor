from django import forms

from webpeditor import settings
from webpeditor_app.models.database import models


class OriginalImageForm(forms.Form):
    image = forms.ImageField(required=True, max_length=settings.MAX_IMAGE_FILE_SIZE)


class EditedImageForm(forms.ModelForm):
    class Meta:
        model = models.EditedImage
        fields = (
            'edited_image_id',
            'original_image_file',
            'edited_image_file',
            'content_type_edited',
            'steps',
            'current_step',
            'edited_image_url',
            'user_id',
            'session_id',
            'session_id_expiration_date',
            'created_at'
        )
