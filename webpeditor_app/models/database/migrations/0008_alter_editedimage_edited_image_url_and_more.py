# Generated by Django 4.1.5 on 2023-02-04 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0007_alter_editedimage_edited_image_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editedimage',
            name='edited_image_url',
            field=models.ImageField(default=None, max_length=6000000, upload_to=''),
        ),
        migrations.AlterField(
            model_name='originalimage',
            name='original_image_url',
            field=models.ImageField(default=None, max_length=6000000, upload_to=''),
        ),
    ]