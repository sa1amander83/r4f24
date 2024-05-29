

import dramatiq

from profiles.models import Statistic


@dramatiq.actor()
def calc_stat(runner_id, dist, tot_time, avg_time, tot_days, tot_runs):
    try:
        run_stat = Statistic.objects.get(runner_stat_id=runner_id)
        run_stat_new = Statistic.objects.filter(runner_stat_id=runner_id).update(
            total_distance=dist,
            total_time=':'.join(str(tot_time).split(':')),
            total_average_temp=':'.join(str(avg_time).split(':')),
            total_days=tot_days,
            total_runs=tot_runs
        )

    except:
        run_stat = Statistic.objects.create(runner_stat_id=runner_id,
                                            total_distance=dist,
                                            total_time=':'.join(str(tot_time).split(':')),
                                            total_average_temp=':'.join(str(avg_time).split(':')),
                                            total_days = tot_days,
                                            total_runs = tot_runs)

    print('ready')

























# from celery import shared_task, Celery
#
# # from core.models import User
# # from profiles.models import RunnerDay
# #
#
# app = Celery('tasks', broker='redis://localhost:6379')
#

#
# @shared_task
# def calc(x,y):
#     return x+y
#
#
# # def total_dist(username):
# #     from django.db.models import Sum
# #     total_distance = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_distance'))
# #     # self.get_ordering(result['day_distance__sum'])
# #     result = total_distance['day_distance__sum']
# #     return result
# #
# #
# # @app.tasks
# # def total_time(username):
# #     from django.db.models import Sum
# #     total_time = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_time'))
# #     return total_time['day_time__sum']
# #
# #
# # @app.tasks
# # def avg_temp(username):
# #     from django.db.models import Avg
# #     result = RunnerDay.objects.filter(runner__username=username).aggregate(Avg('day_average_temp'))
# #     return result['day_average_temp__avg']
# #
# # @app.tasks
# # def calc():
# #     for user in User.objects.all():
# #         print(user)