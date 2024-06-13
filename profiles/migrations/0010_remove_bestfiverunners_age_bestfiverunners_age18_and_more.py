# Generated by Django 5.0.6 on 2024-06-12 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_remove_bestfiverunners_best_runner_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bestfiverunners',
            name='age',
        ),
        migrations.AddField(
            model_name='bestfiverunners',
            name='age18',
            field=models.IntegerField(db_index=True, null=True, verbose_name='возраст до 18'),
        ),
        migrations.AddField(
            model_name='bestfiverunners',
            name='age35',
            field=models.IntegerField(db_index=True, null=True, verbose_name='возраст 18-35'),
        ),
        migrations.AddField(
            model_name='bestfiverunners',
            name='age49',
            field=models.IntegerField(db_index=True, default=0, verbose_name='возраст 36-49'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bestfiverunners',
            name='ageover50',
            field=models.IntegerField(db_index=True, null=True, verbose_name='возраст 50+'),
        ),
        migrations.AlterField(
            model_name='bestfiverunners',
            name='balls',
            field=models.IntegerField(db_index=True, null=True, verbose_name='баллы'),
        ),
        migrations.AlterField(
            model_name='bestfiverunners',
            name='team',
            field=models.IntegerField(db_index=True, null=True, verbose_name='команда'),
        ),
    ]