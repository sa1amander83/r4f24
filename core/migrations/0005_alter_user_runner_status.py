# Generated by Django 5.0.6 on 2024-06-10 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_runner_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='runner_status',
            field=models.IntegerField(choices=[(1, 'Участник'), (2, 'член семьи участника')], default=1, verbose_name='Ваш статус'),
        ),
    ]