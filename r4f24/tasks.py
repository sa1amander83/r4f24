from celery import shared_task, Celery

# from core.models import User
# from profiles.models import RunnerDay
#

app = Celery('tasks', broker='redis://localhost:6379')


@shared_task
def calc(x,y):
    return x+y


# def total_dist(username):
#     from django.db.models import Sum
#     total_distance = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_distance'))
#     # self.get_ordering(result['day_distance__sum'])
#     result = total_distance['day_distance__sum']
#     return result
#
#
# @app.tasks
# def total_time(username):
#     from django.db.models import Sum
#     total_time = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_time'))
#     return total_time['day_time__sum']
#
#
# @app.tasks
# def avg_temp(username):
#     from django.db.models import Avg
#     result = RunnerDay.objects.filter(runner__username=username).aggregate(Avg('day_average_temp'))
#     return result['day_average_temp__avg']
#
# @app.tasks
# def calc():
#     for user in User.objects.all():
#         print(user)