# Generated by Django 4.1.5 on 2023-02-23 15:28

from django.db import migrations, models
import webpeditor_app.services.validators.image_size_validator


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0027_alter_editedimage_edited_image_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editedimage',
            name='edited_image_url',
            field=models.ImageField(default=None, upload_to='edited', validators=[webpeditor_app.services.validators.image_size_validator.validate_image_file_size]),
        ),
    ]