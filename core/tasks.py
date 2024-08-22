from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Count, F, Window, DurationField, Value
from django.db.models.functions import RowNumber
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import ComandsResult, GroupsResult, Group, Teams
from profiles.models import Statistic, Championat


@require_POST
def recalc_all_groups_and_teams(request):
    # Get all groups and teams

    GroupsResult.objects.all().delete()
    ComandsResult.objects.all().delete()
    groups = Group.objects.all()
    teams = Teams.objects.all()

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
        group_total_members = total_group_results.get('tot_members')
        if group_total_members==0:
            GroupsResult.objects.filter(group_id=group_id).delete()

    for team in teams:
        team_id = team.id

        users = get_user_model().objects.filter(runner_team_id=team_id)
        user_stats = Statistic.objects.filter(runner_stat__in=users)
        total_comand_results = user_stats.aggregate(
            total_balls=Sum('total_balls', default=0),
            total_distance=Sum('total_distance', default=0),
            total_time=Sum('total_time', default=Value('00:00:00', output_field=DurationField())),

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
