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
        choices=[('JPEG', 'JPEG'),
                 ('PNG', 'PNG'),
                 ('GIF', 'GIF'),
                 ('WEBP', 'WEBP'),
                 ('BMP', 'BMP'),
                 ('ICO', 'ICO'),
                 ('TIFF', 'TIFF')],

        required=True,
    )
