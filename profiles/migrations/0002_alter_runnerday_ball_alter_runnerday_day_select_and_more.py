# Generated by Django 5.0.6 on 2024-06-16 16:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runnerday',
            name='ball',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='баллы за пробежку'),
        ),
        migrations.AlterField(
            model_name='runnerday',
            name='day_select',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31)], db_index=True, default=16, verbose_name='день пробега'),
        ),
        migrations.AlterField(
            model_name='runnerday',
            name='number_of_run',
            field=models.IntegerField(choices=[(1, 1), (2, 2)], db_index=True, default=1, validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(1)], verbose_name='номер пробежки'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='total_balls',
            field=models.IntegerField(db_index=True, null=True, verbose_name='общая сумма баллов'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='total_days',
            field=models.IntegerField(db_index=True, null=True, verbose_name='дни пробега'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='total_distance',
            field=models.FloatField(blank=True, db_index=True, verbose_name='итоговый пробег'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='total_runs',
            field=models.IntegerField(db_index=True, null=True, verbose_name='количество пробежек'),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='total_time',
            field=models.TimeField(blank=True, db_index=True, verbose_name='общее время пробега'),
        ),
    ]
