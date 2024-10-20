import os
from datetime import datetime

from PIL import Image
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.
from django.urls import reverse
import core
from core.models import User, Teams


class UserImport(models.Model):
    csv_file = models.FileField(upload_to='uploads/')


def user_directory_path(instance, filename):
    runner = instance.runner.username

    subdiv = runner[:3]
    return 'day_of_month/{0}/{1}/{2}/{3}/{4}'.format(subdiv, runner, instance.runner_day.day_select,
                                                     instance.runner_day.number_of_run,
                                                     filename)


class Photo(models.Model):
    runner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Участник", related_name='photos')
    photo = models.FileField(verbose_name="фото", upload_to=user_directory_path, null=True,
                             blank=True, max_length=300)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    runner_day = models.ForeignKey('RunnerDay', on_delete=models.CASCADE, related_name='photos',
                                   verbose_name='день пробежки', null=True)

    def delete(self, *args, **kwargs):
        # До удаления записи получаем необходимую информацию
        storage, path = self.photo.storage, self.photo.path
        # Удаляем сначала модель ( объект )
        super(Photo, self).delete(*args, **kwargs)
        # Потом удаляем сам файл
        storage.delete(path)

    def get_absolute_url(self):
        return reverse('profile:profile', kwargs={'photo': self.photo})

    def __str__(self):
        return f"Photo for {self.runner_day}"


from datetime import date, timedelta


def get_days():
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    return [
        (today.day, today.day),
        (yesterday.day, yesterday.day),
        # (day_before_yesterday.day, day_before_yesterday.day)
    ]


class RunnerDay(models.Model):
    DAYS = ((30, '30 сентября'), (1, '01 октября'), (2, '02 октября'), (3, '03 октября'), (4, '04 октября'),
            (5, '05 октября'), (6, '06 октября'),  (7, '07 октября'), (8, '08 октября'), (9, '09 октября'),
            (10, '10 октября'), (11, '11 октября'),
            (12, '12 октября'), (13, '13 октября'), (14, '14 октября'),
            (15, '15 октября'), (16, '16 октября'), (17, '17 октября'), (18, '18 октября'), (19, '19 октября'),
            (20, '20 октября'), (21, '21 октября'),)

    class Meta:
        verbose_name = 'ежедневный забег'
        verbose_name_plural = "пробеги по дням"

    today = date.today()
    NUM_OF_RUN = [
        (1, 1), (2, 2)
    ]
    runner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='участник', related_name='runner',
                               db_index=True)
    day_select = models.IntegerField(verbose_name='день пробега', choices=DAYS, default=date.today().day,
                                     # day_select = models.IntegerField(verbose_name='день пробега', choices=DAYS, default=date.today().day,
                                     db_index=True)
    day_distance = models.FloatField(verbose_name='дистанция за день', help_text='введите в формате 10,23', null=False,
                                     validators=[MinValueValidator(1), MaxValueValidator(300)], db_index=True)
    day_time = models.TimeField(verbose_name='введите время пробега', help_text='введите в формате 00:00:00')
    day_average_temp = models.TimeField(verbose_name='средний темп', help_text='введите в формате 00:00:00')
    ball = models.IntegerField(verbose_name='баллы за пробежку', blank=True, null=True, db_index=True)
    ball_for_champ = models.IntegerField(verbose_name='баллы с коэффициентом', blank=True, null=True, db_index=True)
    number_of_run = models.IntegerField(verbose_name='номер пробежки', default=1, choices=NUM_OF_RUN, validators=[
        MaxValueValidator(2),
        MinValueValidator(1)
    ], db_index=True)
    run_url = models.URLField(null=True, blank=True, verbose_name="Ссылка на пробег")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время внесения пробежки")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения пробежки")

    def __str__(self):
        return str(self.runner)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.runner})

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     instance = kwargs.get('instance')
    #     if instance:
    #         runner = instance.runner
    #     else:
    #         runner = None
    #
    #     today = datetime.now().day
    #     if runner and runner.category in [1, 2]:
    #         choices = [day for day in RunnerDay.DAYS if day[0] in [today, today - 1]]
    #     elif runner and runner.category == 3:
    #         choices = [day for day in RunnerDay.DAYS if day[0] == today]
    #     else:
    #         choices = RunnerDay.DAYS
    #
    #     self.fields['day_select'].choices = choices


class Statistic(models.Model):
    runner_stat = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='участник', null=False,
                                    related_name='statistics')
    # runner_stat = models.CharField(verbose_name='участник')
    # team = models.IntegerField(verbose_name='команда')
    total_distance = models.FloatField(verbose_name='итоговый пробег', blank=True, db_index=True)
    total_time = models.TimeField(verbose_name='общее время пробега', blank=True, db_index=True)
    total_average_temp = models.TimeField(verbose_name='средний темп за все время', blank=True)
    total_days = models.IntegerField(verbose_name='дни пробега', null=True, db_index=True)
    total_runs = models.IntegerField(verbose_name='количество пробежек', null=True, db_index=True)
    total_balls = models.IntegerField(verbose_name='общая сумма баллов', null=True, db_index=True)
    total_balls_for_champ = models.IntegerField(verbose_name='общая сумма баллов для чемпионата', null=True,
                                                db_index=True)
    is_qualificated = models.BooleanField(verbose_name='прошел квалификацию', default=False)

    def __str__(self):
        return str(self.runner_stat)

    def get_absolute_url(self):
        return reverse('day', kwargs={'day_id': self.pk})

    class Meta:
        verbose_name = 'итоговая статистика'
        verbose_name_plural = "итоговая статистика"

    # def total_dist(self, username):
    #     from django.db.models import Sum
    #
    #     total_distance = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_distance'))
    #     # self.get_ordering(result['day_distance__sum'])
    #     result = total_distance['day_distance__sum']
    #
    #     return result
    #
    # def total_time_(self, username):
    #     from django.db.models import Sum
    #     total_time = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_time'))
    #     return total_time['day_time__sum']
    #
    # def avg_temp(self, username):
    #     from django.db.models import Avg
    #     result = RunnerDay.objects.filter(runner__username=username).aggregate(Avg('day_average_temp'))
    #     return result['day_average_temp__avg']


class Championat(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name='команда', null=True, db_index=True)
    age18 = models.IntegerField(verbose_name='возраст до 18', null=True, db_index=True)
    age35 = models.IntegerField(verbose_name='возраст 18-35', null=True, db_index=True)
    age49 = models.IntegerField(verbose_name='возраст 36-49', db_index=True)
    ageover50 = models.IntegerField(verbose_name='возраст 50+', null=True, db_index=True)
    balls = models.IntegerField(verbose_name='баллы', null=True, db_index=True)

    def __str__(self):
        return str(self.team)
