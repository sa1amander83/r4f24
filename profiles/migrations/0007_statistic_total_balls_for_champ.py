# Generated by Django 5.0.6 on 2024-09-25 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_runnerday_ball_for_champ_alter_runnerday_day_select'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='total_balls_for_champ',
            field=models.IntegerField(db_index=True, null=True, verbose_name='общая сумма баллов для чемпионата'),
        ),
    ]
