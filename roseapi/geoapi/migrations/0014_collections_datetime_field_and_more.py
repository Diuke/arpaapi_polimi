# Generated by Django 5.0.1 on 2024-02-05 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoapi', '0013_remove_airqualitymeasurement_unique_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='collections',
            name='datetime_field',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='collections',
            name='display_fields',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='collections',
            name='filter_fields',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='collections',
            name='geometry_field',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='collections',
            name='geometry_filter_field',
            field=models.TextField(default=None, null=True),
        ),
    ]
