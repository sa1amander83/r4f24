# Generated by Django 5.0.6 on 2024-09-01 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_alter_photo_day_select'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='day_select',
            field=models.IntegerField(null=True, verbose_name='день пробежки'),
        ),
        migrations.AlterField(
            model_name='runnerday',
            name='day_select',
            field=models.IntegerField(choices=[(6, '06.09'), (7, '07.09'), (8, '08.09'), (9, '09.09'), (10, '10.09'), (11, '11.09'), (12, '12.09'), (13, '13.09'), (14, '14.09'), (15, '15.09'), (16, '16.09'), (17, '17.09'), (18, '18.09'), (19, '19.09'), (20, '20.09'), (21, '21.09'), (22, '22.09'), (23, '23.09'), (24, '24.09'), (25, '25.09'), (26, '26.09'), (27, '27.09'), (28, '28.09'), (29, '29.09'), (30, '30.09'), (1, '01.10'), (2, '02.10'), (3, '03.10'), (4, '04.10'), (5, '05.10')], db_index=True, default=1, verbose_name='день пробега'),
        ),
    ]
