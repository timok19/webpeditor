from django import forms

from webpeditor_app.services.validators.image_file_validator import validate_image_file_size


class OriginalImageForm(forms.Form):
    original_image_form = forms.ImageField(
        required=True,
        validators=[validate_image_file_size],
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
