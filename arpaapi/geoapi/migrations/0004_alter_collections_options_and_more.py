# Generated by Django 5.0.1 on 2024-01-29 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoapi', '0003_collections_meteomeasure_meteosensor'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collections',
            options={'verbose_name_plural': 'collections'},
        ),
        migrations.AlterField(
            model_name='airqualitysensor',
            name='date_stop',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='airqualitysensor',
            name='latitude',
            field=models.DecimalField(decimal_places=4, max_digits=8),
        ),
        migrations.AlterField(
            model_name='airqualitysensor',
            name='longitude',
            field=models.DecimalField(decimal_places=4, max_digits=9),
        ),
    ]
