import celery
from celery import shared_task

from celery.worker import request
from django.db import IntegrityError
from django.db.models import Sum, Q, Avg, Count
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver, Signal

from core.models import Teams, User, ComandsResult, GroupsResult, Group
from profiles.models import Statistic, Championat, RunnerDay


# функция обновляет сведения в модели каждые по сумме 5 участников к каждой возрастной категории
# @receiver(pre_save, sender=RunnerDay)
# def my_signal_handler(instance, **kwargs):
#     get_best_five_summ()
#
#
# @receiver(pre_delete, sender=RunnerDay)
# def my_signal_handler(instance, **kwargs):
#     get_best_five_summ()


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def calc_comands(self, username):
    try:
        obj = User.objects.get(username=username)
        if obj:

            team_id = obj.runner_team.id
            try:
                group_id = obj.runner_group.id
                users_group = User.objects.filter(runner_group_id=group_id)
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

                group_obj = GroupsResult.objects.filter(group_id=group_id).update(
                    group_total_balls=total_group_results.get('total_balls'),
                    group_total_distance=total_group_results.get('total_distance'),
                    group_total_time=str(total_group_results.get('total_time')),
                    group_average_temp=str(total_group_results.get('total_average_temp')),
                    group_total_runs=total_group_results.get('total_runs'),
                    group_total_members=total_group_results.get('tot_members'))
            except:
                pass
            users = User.objects.filter(runner_team_id=team_id)
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

            comands_obj = ComandsResult.objects.filter(comand_id=team_id).update(
                comands_total_members=total_comand_results.get('tot_members'),
                comand_total_distance=total_comand_results.get('total_distance'),
                comand_total_balls=total_comand_results.get('total_balls'),
                comand_total_time=str(total_comand_results.get('total_time')),
                comand_average_temp=str(total_comand_results.get('total_average_temp')),
                comand_total_runs=total_comand_results.get('total_runs'))

    except Exception:
        raise Exception()


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def get_best_five_summ(self, username):
    try:
        teams = Teams.objects.filter().values_list('team', flat=True)
        team_id=Teams.objects.get(user__username=username)
        print(team_id)
        age_categories = [
            ('cat1', 5, 17), ('cat2', 18, 35), ('cat3', 36, 49), ('cat4', 50, 99)
        ]
        from django.db.models import Sum, Q, Window, F
        from django.db.models.functions import RowNumber
        from profiles.models import Statistic
        for team in teams:
            team_results = {}
            grand_total = 0

            for category_name, age_start, age_end in age_categories:
                filtered_stats = Statistic.objects.filter(
                    runner_stat__runner_team__team=team,
                    runner_stat__runner_age__gte=age_start,
                    runner_stat__runner_age__lte=age_end
                )

                if not filtered_stats.exists():
                    team_results[category_name] = 0
                    continue

                ranked_stats = filtered_stats.annotate(
                    rank=Window(
                        expression=RowNumber(),
                        order_by=F('total_balls').desc()
                    )
                )

                top_five_stats = ranked_stats.filter(rank__lte=5)
                total_balls = top_five_stats.aggregate(total_balls_sum=Sum('total_balls'))
                total_balls_sum = total_balls.get('total_balls_sum')
                team_results[category_name] = total_balls_sum
                grand_total += total_balls_sum
            try:
               new_rec= Championat.objects.filter(team=team).update(

                    age18=team_results.get('cat1'),
                    age35=team_results.get('cat2'),
                    age49=team_results.get('cat3'),
                    ageover50=team_results.get('cat4'),
                    balls=grand_total)
            except:
                new_rec=Championat.objects.create(
                    team=team,
                    age18=team_results.get('cat1'),
                    age35=team_results.get('cat2'),
                    age49=team_results.get('cat3'),
                    ageover50=team_results.get('cat4'),
                    balls=grand_total)
        calc_comands.delay(username)
    except Exception:
        raise Exception()





@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def calc_start(self, runner_id, username):
    try:
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
            obj = Statistic.objects.get(runner_stat_id=runner_id)
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
        user = username
        get_best_five_summ.delay(username)
    except Exception:
        raise Exception()

    return "success"


# @shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
# def calc_comands(self, username):
#     try:
#         obj = User.objects.select_related('runner_team', 'runner_group').get(username=username)
#         if obj:
#             team_id = obj.runner_team.id
#             group_id = obj.runner_group.id if obj.runner_group else None
#             users_group = User.objects.filter(runner_group_id=group_id)
#             user_group_stats = Statistic.objects.filter(runner_stat__in=users_group).values('runner_stat__age_category').annotate(total_time=Sum('runner_stat__time'), total_distance=Sum('runner_stat__distance'))
#             get_best_five_summ(team_id, user_group_stats)
#     except User.DoesNotExist:
#         pass
#
# def get_best_five_summ(team_id, user_group_stats):
#     # Your code to calculate the best five participants in each age category
#     pass