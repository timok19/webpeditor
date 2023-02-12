# Generated by Django 4.1.5 on 2023-02-12 15:12

from django.db import migrations, models
import webpeditor_app.services.validators.image_size_validator


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0012_rename_original_image_editedimage_original_image_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='originalimage',
            name='original_image_url',
            field=models.ImageField(default=None, upload_to='', validators=[webpeditor_app.services.validators.image_size_validator.validate_image_file_size]),
        ),
    ]
