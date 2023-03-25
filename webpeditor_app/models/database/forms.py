from django import forms

from webpeditor import settings


class OriginalImageForm(forms.Form):
    original_image_form = forms.ImageField(
        required=True,
        max_length=settings.MAX_IMAGE_FILE_SIZE,
        allow_empty_file=False
    )
