from cloudinary.forms import CloudinaryFileField
from django import forms


class OriginalImageAssetForm(forms.Form):
    image = forms.ImageField(required=True, allow_empty_file=False)


class ConvertedImageAssetForm(forms.Form):
    image = CloudinaryFileField(
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
    quality = forms.IntegerField(
        required=True,
        step_size=5,
        min_value=5,
        max_value=100,
        initial=50,
        widget=forms.NumberInput(attrs={"type": "range"}),
        disabled=True,
    )
