# Generated by Django 5.0.6 on 2024-06-04 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_statistic_ball_alter_photo_day_select_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistic',
            name='ball',
        ),
        migrations.AddField(
            model_name='runnerday',
            name='ball',
            field=models.IntegerField(blank=True, null=True, verbose_name='баллы'),
        ),
    ]
