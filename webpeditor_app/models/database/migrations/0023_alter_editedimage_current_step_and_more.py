# Generated by Django 4.1.5 on 2023-02-22 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0022_editedimage_current_step_editedimage_steps_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editedimage',
            name='current_step',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='editedimage',
            name='edited_image_file',
            field=models.CharField(default='<django.db.models.query_utils.DeferredAttribute object at 0x000001E5BA2F8EE0>', max_length=255),
        ),
    ]
