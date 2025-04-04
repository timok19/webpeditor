# Generated by Django 5.1.5 on 2025-02-02 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webpeditor_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='converterconvertedimageassetfile',
            name='aspect_ratio',
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='converteroriginalimageassetfile',
            name='aspect_ratio',
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='editoreditedimageassetfile',
            name='aspect_ratio',
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='editororiginalimageassetfile',
            name='aspect_ratio',
            field=models.DecimalField(decimal_places=2, max_digits=4, null=True),
        ),
    ]
