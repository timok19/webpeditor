from django import forms

from webpeditor import settings


class OriginalImageForm(forms.Form):
    image = forms.ImageField(required=True, max_length=settings.MAX_IMAGE_FILE_SIZE)
