# Generated by Django 5.0.6 on 2024-06-10 12:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_alter_runnerday_day_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runnerday',
            name='day_distance',
            field=models.FloatField(help_text='введите в формате 10,23', validators=[django.core.validators.MinValueValidator(1)], verbose_name='дистанция за день'),
        ),
    ]