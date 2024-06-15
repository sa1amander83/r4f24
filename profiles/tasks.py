from celery import shared_task
from django.db import IntegrityError
from django.db.models import Sum, Q, Avg
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver, Signal

from core.models import Teams, User
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

@shared_task
def get_best_five_summ():
    teams = Teams.objects.values_list('team', flat=True)
    my_list = []
    my_dict = {}
    d = dict()
    age_categories = [
        # (f'до {age} лет', age) for age in range(18, 80, 17)
        ('cat1', 5, 17), ("cat2", 18, 35), ("cat3", 36, 49), ("cat4", 50, 99)
    ]
    from django.db.models import Sum, Q, Window, F
    from django.db.models.functions import RowNumber
    from profiles.models import Statistic
    for team in teams:
        team_results = {}
        grand_total = 0  # Initialize a variable to keep track of the grand total across all categories for the current team

        for category_name, age_start, age_end in age_categories:
            # Filter participants within the age range and belonging to the current team
            filtered_stats = Statistic.objects.filter(
                runner_stat__runner_team=team,
                runner_stat__runner_age__gte=age_start,
                runner_stat__runner_age__lte=age_end
            )

            # Annotate each participant with a rank based on total_balls in descending order
            ranked_stats = filtered_stats.annotate(
                rank=Window(
                    expression=RowNumber(),
                    order_by=F('total_balls').desc()
                )
            )

            # Filter to get only the top 5 participants
            top_five_stats = ranked_stats.filter(rank__lte=5)

            # Aggregate the total balls of the top five participants
            total_balls = top_five_stats.aggregate(total_balls_sum=Sum('total_balls'))

            # Store the results in a dictionary
            total_balls_sum = total_balls['total_balls_sum'] if total_balls['total_balls_sum'] is not None else 0
            team_results[category_name] = total_balls_sum

            # Add to the grand total
            grand_total += total_balls_sum

        # Update or create in BestFiveRunners
        best_five, created = BestFiveRunners.objects.update_or_create(
            team=team,  # Use the team ID as the unique identifier
            defaults={
                'age18': team_results.get('cat1', 0),
                'age35': team_results.get('cat2', 0),
                'age49': team_results.get('cat3', 0),
                'ageover50': team_results.get('cat4', 0),
                'balls': grand_total
            }
        )
    return "success"


# @receiver(post_save,sender=RunnerDay)
# def my_signal_handler(instance, **kwargs):
#     calc_start.delay(instance.runner.id, instance.runner.username)
#     print(123)
#
# @receiver(post_delete,sender=RunnerDay)
# def my_signal_handler(instance, **kwargs):
#     calc_start.delay(instance.runner.id, instance.runner.username)
#     print(321)


@shared_task()
def calc_start(runner_id, username):
    total_distance = RunnerDay.objects.filter(runner__username=username).aggregate(
        Sum('day_distance'))
    if total_distance['day_distance__sum'] is None:
        dist = 0
    else:
        dist = total_distance['day_distance__sum']

    total_time = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('day_time'))
    if total_time['day_time__sum'] is None:
        tot_time = '00:00'
    else:
        tot_time = total_time['day_time__sum']
    # avg_time = self.avg_temp_function(username)
    avg_time = RunnerDay.objects.filter(runner__username=username).aggregate(Avg('day_average_temp'))

    if avg_time['day_average_temp__avg'] is None:
        avg_time = '00:00'
    else:
        avg_time = avg_time['day_average_temp__avg']

    tot_runs = RunnerDay.objects.filter(runner__username=username).filter(
        day_distance__gte=0).count()
    tot_days = RunnerDay.objects.filter(runner__username=username).filter(
        day_select__gte=0).distinct('day_select').count()
    tot_balls = RunnerDay.objects.filter(runner__username=username).aggregate(Sum('ball'))
    if tot_balls['ball__sum'] is None:
        balls = 0
    else:
        balls = tot_balls['ball__sum']
    is_qual = True if dist >= 30 else False

    try:
        obj=Statistic.objects.get(runner_stat_id=runner_id)
        Statistic.objects.filter(id=obj.pk).update(
        total_distance=dist,
        total_time=':'.join(str(tot_time).split(':')),
        total_average_temp=':'.join(str(avg_time).split(':')),
        total_days=tot_days,
        total_runs=tot_runs,
        total_balls=balls,
        is_qualificated=is_qual)


    except:
        Statistic.objects.create(
            runner_stat_id=runner_id,
            total_distance=dist,
            total_time=':'.join(str(tot_time).split(':')),
            total_average_temp=':'.join(str(avg_time).split(':')),
            total_days=tot_days,
            total_runs=tot_runs,
            total_balls=balls,
            is_qualificated=is_qual)

    return "success"
