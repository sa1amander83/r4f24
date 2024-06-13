# Generated by Django 5.0.6 on 2024-06-12 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0008_alter_runnerday_day_select_bestfiverunners'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bestfiverunners',
            name='best_runner',
        ),
        migrations.AddField(
            model_name='bestfiverunners',
            name='team',
            field=models.IntegerField(default=0, verbose_name='команда'),
            preserve_default=False,
        ),
    ]