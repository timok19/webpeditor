# Generated by Django 5.1.2 on 2024-11-02 00:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("webpeditor_app", "0009_remove_convertedimage_image_file_convertedimagefile"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="convertedimagefile",
            options={"verbose_name": "Converted Image File", "verbose_name_plural": "Converted Image Files"},
        ),
    ]
