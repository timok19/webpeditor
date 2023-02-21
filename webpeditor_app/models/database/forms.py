from PIL import Image
from django import forms

from webpeditor import settings


class OriginalImageForm(forms.Form):
    image = forms.ImageField(required=True, max_length=settings.MAX_IMAGE_FILE_SIZE)


class EditedImageForm(forms.Form):
    file = forms.ImageField()
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    def save(self):
        cleaned_data = super().clean()
        file = cleaned_data['file']
        x = cleaned_data['x']
        y = cleaned_data['y']
        w = cleaned_data['width']
        h = cleaned_data['height']

        image = Image.open(file)
        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(file.name, format='JPEG', quality=90)

        return file
