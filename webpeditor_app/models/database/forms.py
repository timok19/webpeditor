from django import forms

from webpeditor import settings
from webpeditor_app.models.database import models


class OriginalImageForm(forms.Form):
    image = forms.ImageField(required=True, max_length=settings.MAX_IMAGE_FILE_SIZE)


class EditedImageForm(forms.Form):
    image = forms.CharField(max_length=settings.MAX_IMAGE_FILE_SIZE)
