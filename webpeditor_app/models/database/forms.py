from django import forms
from django.forms import HiddenInput

from webpeditor import settings


class OriginalImageForm(forms.Form):
    original_image_form = forms.ImageField(
        required=True,
        max_length=settings.MAX_IMAGE_FILE_SIZE,
        allow_empty_file=False
    )


class EditedImageForm(forms.Form):
    edited_image_form = forms.ImageField(
        required=False,
        max_length=settings.MAX_IMAGE_FILE_SIZE,
        widget=HiddenInput()
    )
