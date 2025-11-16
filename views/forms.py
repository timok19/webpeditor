from django import forms
from django.forms import ImageField, IntegerField


class OriginalImageAssetForm(forms.Form):
    image: ImageField = forms.ImageField(required=True)


class ImageConverterUploadFilesForm(forms.Form):
    image: ImageField = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}),
    )
    output_format = forms.ChoiceField(
        choices=[
            ("WEBP", ".webp"),
            ("JPEG", ".jpeg"),
            ("PNG", ".png"),
            ("GIF", ".gif"),
            ("BMP", ".bmp"),
            ("ICO", ".ico"),
            ("TIFF", ".tiff"),
        ],
        required=True,
    )
    quality: IntegerField = forms.IntegerField(
        required=True,
        min_value=5,
        max_value=100,
        initial=50,
        widget=forms.NumberInput(attrs={"type": "range"}),
        disabled=True,
    )
