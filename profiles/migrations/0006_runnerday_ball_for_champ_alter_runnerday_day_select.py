# Generated by Django 5.0.6 on 2024-09-25 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_alter_runnerday_day_select'),
    ]

    operations = [
        migrations.AddField(
            model_name='runnerday',
            name='ball_for_champ',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='баллы с коэффициентом'),
        ),
        migrations.AlterField(
            model_name='runnerday',
            name='day_select',
            field=models.IntegerField(choices=[(25, 25), (24, 24)], db_index=True, default=25, verbose_name='день пробега'),
        ),
    ]