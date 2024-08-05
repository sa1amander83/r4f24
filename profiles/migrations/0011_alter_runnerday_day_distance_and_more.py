# Generated by Django 5.0.6 on 2024-08-04 18:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_alter_runnerday_day_select'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runnerday',
            name='day_distance',
            field=models.FloatField(db_index=True, help_text='введите в формате 10,23', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(300)], verbose_name='дистанция за день'),
        ),
        migrations.AlterField(
            model_name='runnerday',
            name='day_select',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31)], db_index=True, default=4, verbose_name='день пробега'),
        ),
    ]
