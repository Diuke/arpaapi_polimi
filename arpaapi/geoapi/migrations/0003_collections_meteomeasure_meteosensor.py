# Generated by Django 5.0.1 on 2024-01-29 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoapi', '0002_rename_airqualitystation_airqualitysensor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collections',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('model_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MeteoMeasure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='MeteoSensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
