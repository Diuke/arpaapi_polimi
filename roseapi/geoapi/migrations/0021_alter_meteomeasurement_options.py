# Generated by Django 5.0.1 on 2024-02-09 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "geoapi",
            "0020_alter_meteomeasurement_options_meteomeasurement_date_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="meteomeasurement",
            options={"verbose_name_plural": "Meteorological Measurements"},
        ),
    ]