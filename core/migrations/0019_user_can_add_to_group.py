# Generated by Django 5.0.6 on 2024-08-17 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_user_runner_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='can_add_to_group',
            field=models.BooleanField(default=False, null=True, verbose_name='Участник группы'),
        ),
    ]
