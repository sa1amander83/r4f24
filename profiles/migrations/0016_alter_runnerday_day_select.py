# Generated by Django 5.0.6 on 2024-10-05 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_alter_photo_runner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runnerday',
            name='day_select',
            field=models.IntegerField(choices=[(5, 5), (4, 4)], db_index=True, default=5, verbose_name='день пробега'),
        ),
    ]