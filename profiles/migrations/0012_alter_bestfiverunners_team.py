# Generated by Django 5.0.6 on 2024-06-12 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_alter_bestfiverunners_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bestfiverunners',
            name='team',
            field=models.IntegerField(db_index=True, null=True, verbose_name='команда'),
        ),
    ]
