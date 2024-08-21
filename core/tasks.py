from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Count, F, Window
from django.db.models.functions import RowNumber

from core.models import ComandsResult, GroupsResult, Group, Teams
from profiles.models import Statistic, Championat


# def get_best_five_summ():
#
#     try:
#         age_categories = [
#             ('cat1', 5, 17), ('cat2', 18, 35), ('cat3', 36, 49), ('cat4', 50, 99)
#         ]
#
#         team_results = {}
#         grand_total = 0
#
#         for category_name, age_start, age_end in age_categories:
#             filtered_stats = Statistic.objects.filter(
#                 runner_stat__runner_age__gte=age_start,
#                 runner_stat__runner_age__lte=age_end
#             )
#
#             if not filtered_stats.exists():
#                 team_results[category_name] = 0
#                 continue
#
#             ranked_stats = filtered_stats.annotate(
#                 rank=Window(
#                     expression=RowNumber(),
#                     order_by=F('total_balls').desc()
#                 )
#             )
#
#             top_five_stats = ranked_stats.filter(rank__lte=5)
#             total_balls = top_five_stats.aggregate(total_balls_sum=Sum('total_balls'))
#             total_balls_sum = total_balls.get('total_balls_sum')
#             team_results[category_name] = total_balls_sum
#             grand_total += total_balls_sum
#
#         Championat.objects.update_or_create(
#             team_id=team.id,
#             defaults={
#                 'age18': team_results.get('cat1'),
#                 'age35': team_results.get('cat2'),
#                 'age49': team_results.get('cat3'),
#                 'ageover50': team_results.get('cat4'),
#                 'balls': grand_total
#             }
#         )
#
#     except Exception:
#         raise
#
@shared_task
def calc_comands():
    all_groups=Group.objects.all()
    for group in all_groups:
        users_group = get_user_model().objects.filter(runner_group_id=group.id)
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
            group_id=group.id,
            defaults={
                'group_total_balls': total_group_results.get('total_balls'),
                'group_total_distance': total_group_results.get('total_distance'),
                'group_total_time': str(total_group_results.get('total_time')),
                'group_average_temp': str(total_group_results.get('total_average_temp')),
                'group_total_runs': total_group_results.get('total_runs'),
                'group_total_members': total_group_results.get('tot_members')
            }
        )


    all_teams=Teams.objects.all()

    for team in all_teams:


        users = get_user_model().objects.filter(runner_team_id=team.id)
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
            comand_id=team.id,
            defaults={
                'comands_total_members': total_comand_results.get('tot_members'),
                'comand_total_distance': total_comand_results.get('total_distance'),
                'comand_total_balls': total_comand_results.get('total_balls'),
                'comand_total_time': str(total_comand_results.get('total_time')),
                'comand_average_temp': str(total_comand_results.get('total_average_temp')),
                'comand_total_runs': total_comand_results.get('total_runs')
            }
        )
    # get_best_five_summ()



def recalc_all_groups_and_teams(request):
    # Get all groups and teams

    GroupsResult.objects.all().delete()
    ComandsResult.objects.all().delete()
    groups = Group.objects.all()
    teams = Teams.objects.all()

    # Recalculate results for each group
    for group in groups:
        group_id = group.id
        users_group = get_user_model().objects.filter(runner_group_id=group_id)
        user_group_stats = Statistic.objects.filter(runner_stat__in=users_group)
        total_group_results = user_group_stats.aggregate(
            total_balls=Sum('total_balls', default=0),
            total_distance=Sum('total_distance', default=0),
            total_time=Sum('total_time', default=Value('00:00:00', output_field=DurationField())),
            total_average_temp=Avg('total_average_temp', default=Value('00:00:00', output_field=DurationField())),
            total_days=Sum('total_days', default=0),
            total_runs=Sum('total_runs', default=0),
            tot_members=Count('runner_stat__username')
        )

        GroupsResult.objects.create(
            group_id=group_id,
            group_total_balls=total_group_results.get('total_balls'),
            group_total_distance=total_group_results.get('total_distance'),
            group_total_time=str(total_group_results.get('total_time')),
            group_average_temp=str(total_group_results.get('total_average_temp')),
            group_total_runs=total_group_results.get('total_runs'),
            group_total_members=total_group_results.get('tot_members')
        )

    # Recalculate results for each team
    for team in teams:
        team_id = team.id

        users = get_user_model().objects.filter(runner_team_id=team_id)
        user_stats = Statistic.objects.filter(runner_stat__in=users)
        total_comand_results = user_stats.aggregate(
            total_balls=Sum('total_balls', default=0),
            total_distance=Sum('total_distance', default=0),
            total_time=Sum('total_time', default=Value('00:00:00', output_field=DurationField())),
            # note the use of Value and DurationField
            total_average_temp=Avg('total_average_temp', default=Value('00:00:00', output_field=DurationField())),
            total_days=Sum('total_days', default=0),
            total_runs=Sum('total_runs', default=0),
            tot_members=Count('runner_stat__username'))

        ComandsResult.objects.create(
            comand_id=team_id,
      
            comands_total_members=total_comand_results.get('tot_members'),
            comand_total_distance=total_comand_results.get('total_distance'),
            comand_total_balls=total_comand_results.get('total_balls'),
            comand_total_time=str(total_comand_results.get('total_time')),
            comand_average_temp=str(total_comand_results.get('total_average_temp')),
            comand_total_runs=total_comand_results.get('total_runs')

        )

    return redirect(reverse('index'))
