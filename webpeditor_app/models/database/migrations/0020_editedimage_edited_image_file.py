# Generated by Django 4.1.5 on 2023-02-21 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0019_alter_editedimage_edited_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='editedimage',
            name='edited_image_file',
            field=models.CharField(default=None, max_length=255),
        ),
    ]