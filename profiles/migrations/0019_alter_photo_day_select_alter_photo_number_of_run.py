# Generated by Django 5.0.6 on 2024-06-05 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_photo_day_select_photo_number_of_run'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='day_select',
            field=models.IntegerField(null=True, verbose_name='день пробежки'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='number_of_run',
            field=models.IntegerField(null=True, verbose_name='номер пробежки'),
        ),
    ]