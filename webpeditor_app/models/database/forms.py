from django import forms


class OriginalImageForm(forms.Form):
    original_image_form = forms.ImageField(
        required=True,
        allow_empty_file=False
    )


class ImagesToConvertForm(forms.Form):
    images_to_convert = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )
    output_format = forms.ChoiceField(
        choices=[('WEBP', 'WEBP'),
                 ('JPEG', 'JPEG'),
                 ('PNG', 'PNG'),
                 ('GIF', 'GIF'),
                 ('BMP', 'BMP'),
                 ('ICO', 'ICO'),
                 ('TIFF', 'TIFF')],
        required=True
    )
    quality = forms.IntegerField(
        required=True,
        min_value=5,
        max_value=100,
        initial=50,
        widget=forms.NumberInput(attrs={'type': 'range'})
    )
