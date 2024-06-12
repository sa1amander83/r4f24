from django.db import IntegrityError
from django.db.models import Sum, Q
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver, Signal

from core.models import Teams
from profiles.models import Statistic, BestFiveRunners, RunnerDay


# TODO  эту функцию через селери запускать после каждого внесения данных о пробежке
# функция обновляет сведения в модели каждые по сумме 5 участников к каждой возрастной категории
# @receiver(pre_save, sender=RunnerDay)
# def my_signal_handler(instance, **kwargs):
#     get_best_five_summ()
#
#
# @receiver(pre_delete, sender=RunnerDay)
# def my_signal_handler(instance, **kwargs):
#     get_best_five_summ()


def get_best_five_summ():
    teams = Teams.objects.values_list('team', flat=True)
    my_list = []
    my_dict = {}
    d = dict()
    age_categories = [
        # (f'до {age} лет', age) for age in range(18, 80, 17)
        ('cat1', 5, 17), ("cat2", 18, 35), ("cat3", 36, 49), ("cat4", 50, 99)
    ]

    category_name = ''
    ball_summ_in_category = 0
    summ = 0
    balls = 0
    for team in teams:
        for category_name, category_age_start, category_age_end in age_categories:
            # сумма баллов в каждой категории
            ball_summ_in_category = Statistic.objects.filter(runner_stat__runner_team=team).filter(
                Q(runner_stat__runner_age__gte=category_age_start),
                Q(runner_stat__runner_age__lte=category_age_end)
            ).order_by('-total_balls')[:5].annotate(total_ball=Sum('total_balls')).aggregate(Sum('total_ball'))

            if ball_summ_in_category['total_ball__sum'] is None:
                balls = 0
            else:
                balls = ball_summ_in_category['total_ball__sum']
            summ = summ + balls
            my_list.append(balls)
        try:
            BestFiveRunners.objects.create(team=team,
                                            age18=my_list[0],
                                            age35=my_list[1],
                                            age49=my_list[2],
                                            ageover50=my_list[3],
                                            balls=summ)
        except IntegrityError:
            pass
            # BestFiveRunners.objects.update(team=team,
            #                                 age18=my_list[0],
            #                                 age35=my_list[1],
            #                                 age49=my_list[2],
            #                                 ageover50=my_list[3],
            #                                 balls=summ)
        # d[team] = {'age': my_list, 'summ': summ}
        balls = 0
        my_list = []
        summ = 0

# rabbitmq_broker = RabbitmqBroker(host="rabbitmq")
# dramatiq.set_broker(rabbitmq_broker)
#
# @dramatiq.actor()
# def calc_stat(runner_id, dist, tot_time, avg_time, tot_days, tot_runs):
#     try:
#         run_stat = Statistic.objects.get(runner_stat_id=runner_id)
#         run_stat_new = Statistic.objects.filter(runner_stat_id=runner_id).update(
#             total_distance=dist,
#             total_time=':'.join(str(tot_time).split(':')),
#             total_average_temp=':'.join(str(avg_time).split(':')),
#             total_days=tot_days,
#             total_runs=tot_runs
#         )
#
#     except:
#         run_stat = Statistic.objects.create(runner_stat_id=runner_id,
#                                             total_distance=dist,
#                                             total_time=':'.join(str(tot_time).split(':')),
#                                             total_average_temp=':'.join(str(avg_time).split(':')),
#                                             total_days = tot_days,
#                                             total_runs = tot_runs)
#
#     print('ready')
#


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
