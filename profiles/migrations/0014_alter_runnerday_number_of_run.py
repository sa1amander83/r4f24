# Generated by Django 5.0.6 on 2024-06-05 06:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_runnerday_number_of_run_alter_photo_day_select_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runnerday',
            name='number_of_run',
            field=models.IntegerField(choices=[(1, 1), (2, 2)], default=1, validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(1)], verbose_name='номер пробежки'),
        ),
    ]
