# Generated by Django 4.1.5 on 2023-02-21 14:17

from django.db import migrations, models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0021_alter_editedimage_edited_image_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='editedimage',
            name='current_step',
            field=models.IntegerField(default=0, max_length=50),
        ),
        migrations.AddField(
            model_name='editedimage',
            name='steps',
            field=django_extensions.db.fields.json.JSONField(blank=True, default=list, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='editedimage',
            name='edited_image_file',
            field=models.CharField(default='<django.db.models.query_utils.DeferredAttribute object at 0x000001C6D0D0A410>', max_length=255),
        ),
    ]
