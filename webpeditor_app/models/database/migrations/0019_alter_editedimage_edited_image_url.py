# Generated by Django 4.1.5 on 2023-02-21 10:23

from django.db import migrations
import imagekit.models.fields
import webpeditor_app.services.validators.image_file_validator


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0018_rename_user_folder_name_editedimage_user_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editedimage',
            name='edited_image_url',
            field=imagekit.models.fields.ProcessedImageField(default=None, upload_to='edited', validators=[webpeditor_app.services.validators.image_file_validator.validate_image_file_size]),
        ),
    ]
