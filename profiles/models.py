from datetime import datetime

from django.db import models

# Create your models here.
from django.urls import reverse

from core.models import User

def user_directory_path(instance, filename):
    runner = instance.runner.user.username
    subdiv = runner[:3]
    return 'day_of_month/{0}/{1}/{2}/{3}'.format(instance.day_select, subdiv, runner, filename)

class RunnerDay(models.Model):
    class Meta:
        verbose_name = 'ежедневный забег'
        verbose_name_plural = "пробеги по дням"

    days= range(1,32)
    DAYS =[(i,i) for i in days]
    url=models.SlugField()
    runner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='участник', related_name='runner')
    day_select = models.IntegerField(verbose_name='день пробега', choices=DAYS, default=datetime.now().day)
    day_distance = models.FloatField(verbose_name='дистанция за день', help_text='введите в формате 10,23', null=False)
    day_time = models.TimeField(verbose_name='введите время пробега',help_text='введите в формате 00:00:00')
    day_average_temp = models.TimeField(verbose_name='средний темп', help_text='введите в формате 00:00:00')
    photo = models.ImageField(verbose_name="фото", upload_to=user_directory_path, null=True,
                              blank=True, max_length=300)
    calory = models.IntegerField(verbose_name='Потрачено калорий',null=True, blank=True)

    def __str__(self):
        return str(self.runner)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.runner})