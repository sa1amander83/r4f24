from random import random

from celery import shared_task

from django.apps import apps


@shared_task
def calc(x,y):
    # RunnerDay = apps.get_model('runnerdays', 'RunnerDay')
    # Statistic=apps.get_model('statistics','Statistic')
    #
    # Statistic.objects.get_or_create()



   return print(calc(random(1,10)*random(1,20)))
