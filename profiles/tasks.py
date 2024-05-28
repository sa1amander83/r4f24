from random import random

from celery import shared_task

from django.apps import apps

from profiles.models import Statistic


@shared_task
def calc_stat(runner_id, dist, tot_time, avg_time):
    try:
        run_stat=Statistic.objects.get(runner_stat_id=runner_id)
        run_stat_new = Statistic.objects.filter(runner_stat_id=runner_id).update(
            total_distance=dist,
            total_time=':'.join(str(tot_time).split(':')),
            total_average_temp=':'.join(str(avg_time).split(':'))
        )

    except:
        run_stat = Statistic.objects.create(runner_stat_id=runner_id,
                                            total_distance=dist,
                                            total_time=':'.join(str(tot_time).split(':')),
                                            total_average_temp=':'.join(str(avg_time).split(':')))


    print('ready')


