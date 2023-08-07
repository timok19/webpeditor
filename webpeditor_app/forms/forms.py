from django import forms


class OriginalImageForm(forms.Form):
    original_image_form = forms.ImageField(required=True, allow_empty_file=False)


class ImagesToConvertForm(forms.Form):
    images_to_convert = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}),
    )
    # TODO: need to fix the form with multiple upload in asgi application
    output_format = forms.ChoiceField(
        choices=[
            ("WEBP", "WEBP"),
            ("JPEG", "JPEG"),
            ("PNG", "PNG"),
            ("GIF", "GIF"),
            ("BMP", "BMP"),
            ("ICO", "ICO"),
            ("TIFF", "TIFF"),
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
