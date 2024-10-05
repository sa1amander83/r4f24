from celery import shared_task
from celery.schedules import crontab
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import CreateError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q, Avg, Count, Window, F
from django.db.models.functions import RowNumber
from core.models import User, ComandsResult, GroupsResult, Teams, Group
from profiles.models import Statistic, Championat, RunnerDay
from r4f24.celery import app

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def get_best_five_summ(self,team_id):
    try:
        age_categories = [
            ('cat1', 5, 17), ('cat2', 18, 35), ('cat3', 36, 49), ('cat4', 50, 99)]

        team_results = {}
        grand_total = 0

        # Filter the statistics for the specified team and age range
        for category_name, age_start, age_end in age_categories:
            filtered_stats = Statistic.objects.filter(
                runner_stat__runner_team_id=team_id,
                runner_stat__runner_age__gte=age_start,
                runner_stat__runner_age__lte=age_end
            )

            if not filtered_stats.exists():
                team_results[category_name] = 0
                continue

            ranked_stats = filtered_stats.annotate(
                rank=Window(
                    expression=RowNumber(),
                    order_by=F('total_balls_for_champ').desc()
                )
            )

            top_five_stats = ranked_stats.filter(rank__lte=5)
            total_balls = top_five_stats.aggregate(total_balls_sum=Sum('total_balls_for_champ'))

            total_balls_sum = total_balls.get('total_balls_sum')
            team_results[category_name] = total_balls_sum
            grand_total += total_balls_sum


        Championat.objects.update_or_create(
            team_id=team_id,
            defaults={
                'age18': team_results.get('cat1'),
                'age35': team_results.get('cat2'),
                'age49': team_results.get('cat3'),
                'ageover50': team_results.get('cat4'),
                'balls': grand_total
            }
        )


    except Exception:
        raise

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def calc_comands(self,username):
    obj = get_user_model().objects.get(username=username)
    try:
        if obj.runner_group is not None:
            group_id = obj.runner_group.id
            users_group = get_user_model().objects.filter(runner_group_id=group_id)
            user_group_stats = Statistic.objects.filter(runner_stat__in=users_group)
            total_group_results = user_group_stats.aggregate(
                total_balls=Sum('total_balls'),
                total_distance=Sum('total_distance'),
                total_time=Sum('total_time'),
                total_average_temp=Avg('total_average_temp'),
                total_days=Sum('total_days'),
                total_runs=Sum('total_runs'),
                tot_members=Count('runner_stat__username')
            )

            GroupsResult.objects.update_or_create(
                group_id=group_id,
                defaults={
                    'group_total_balls': total_group_results.get('total_balls'),
                    'group_total_distance': total_group_results.get('total_distance'),
                    'group_total_time': str(total_group_results.get('total_time')),
                    'group_average_temp': str(total_group_results.get('total_average_temp')),
                    'group_total_runs': total_group_results.get('total_runs'),
                    'group_total_members': total_group_results.get('tot_members')
                }
            )
            print('groups done')
        team_id = obj.runner_team.id

        users = get_user_model().objects.filter(runner_team_id=team_id)
        user_stats = Statistic.objects.filter(runner_stat__in=users)
        total_comand_results = user_stats.aggregate(
            total_balls=Sum('total_balls'),
            total_distance=Sum('total_distance'),
            total_time=Sum('total_time'),
            total_average_temp=Avg('total_average_temp'),
            total_days=Sum('total_days'),
            total_runs=Sum('total_runs'),
            tot_members=Count('runner_stat__username')
        )

        ComandsResult.objects.update_or_create(
            comand_id=team_id,
            defaults={
                'comands_total_members': total_comand_results.get('tot_members'),
                'comand_total_distance': total_comand_results.get('total_distance'),
                'comand_total_balls': total_comand_results.get('total_balls'),
                'comand_total_time': str(total_comand_results.get('total_time')),
                'comand_average_temp': str(total_comand_results.get('total_average_temp')),
                'comand_total_runs': total_comand_results.get('total_runs')
            }
        )

    except Exception:
        raise

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
# @shared_task()
def calc_start(self, runner_id, username):
    try:
        runner_days = RunnerDay.objects.filter(runner__username=username)
        total_distance = runner_days.aggregate(Sum('day_distance'))
        dist = total_distance['day_distance__sum'] or 0

        total_time = runner_days.aggregate(Sum('day_time'))
        tot_time = total_time['day_time__sum'] or '00:00'

        avg_time = runner_days.aggregate(Avg('day_average_temp'))
        avg_time = avg_time['day_average_temp__avg'] or '00:00'

        tot_runs = runner_days.filter(day_distance__gte=0).count()
        tot_days = runner_days.filter(day_select__gte=0).distinct('day_select').count()

        tot_balls = runner_days.aggregate(Sum('ball'))
        tot_balls_champ = runner_days.aggregate(Sum('ball_for_champ'))


        balls = tot_balls['ball__sum'] or 0
        balls_champ = tot_balls_champ['ball_for_champ__sum'] or 0

        is_qual = dist >= 50

        Statistic.objects.update_or_create(
            runner_stat_id=runner_id,
            defaults={
                'total_distance': dist,
                'total_time': ':'.join(str(tot_time).split(':')),
                'total_average_temp': ':'.join(str(avg_time).split(':')),
                'total_days': tot_days,
                'total_runs': tot_runs,
                'total_balls': balls,
                'total_balls_for_champ': balls_champ,
                'is_qualificated': is_qual
            }
        )
        # calc_comands.delay(username)
    except CreateError:
        pass




