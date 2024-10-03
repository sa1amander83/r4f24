from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Count, F, Window, DurationField, Value
from django.db.models.functions import RowNumber
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import ComandsResult, GroupsResult, Group, Teams
from profiles.models import Statistic, Championat, RunnerDay

from datetime import timedelta


@require_POST
def recalc_all_groups_and_teams(request):
    # Удаление старых результатов
    GroupsResult.objects.all().delete()
    ComandsResult.objects.all().delete()

    groups = Group.objects.all()
    teams = Teams.objects.all()

    def format_duration(duration):
        """Helper function to format timedelta to 'HH:MM:SS'."""
        if duration is not None:
            if isinstance(duration, timedelta):
                total_seconds = int(duration.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{hours:02}:{minutes:02}:{seconds:02}"
            elif isinstance(duration, str):
                return duration  # Assuming it's already formatted
        return "00:00:00"

    for group in groups:
        group_id = group.id
        users_group = get_user_model().objects.filter(runner_group_id=group_id)
        user_group_stats = Statistic.objects.filter(runner_stat__in=users_group)

        total_group_results = user_group_stats.aggregate(
            total_balls=Sum('total_balls', default=0),
            total_distance=Sum('total_distance', default=0),
            total_time=Sum('total_time'),
            total_average_temp=Avg('total_average_temp', default=0),
            total_days=Sum('total_days', default=0),
            total_runs=Sum('total_runs', default=0),
            tot_members=Count('runner_stat__username')
        )

        group_total_members = total_group_results.get('tot_members', 0)

        # Создание записи для группы только если есть участники
        if group_total_members > 0:
            GroupsResult.objects.create(
                group_id=group_id,
                group_total_balls=total_group_results.get('total_balls', 0),
                group_total_distance=total_group_results.get('total_distance', 0),
                group_total_time=format_duration(total_group_results.get('total_time')),
                group_average_temp=total_group_results.get('total_average_temp', 0),
                group_total_runs=total_group_results.get('total_runs', 0),
                group_total_members=group_total_members
            )
        else:
            # Если нет участников, удаляем запись группы (если она была создана ранее)
            GroupsResult.objects.filter(group_id=group_id).delete()

    for team in teams:
        team_id = team.id
        users = get_user_model().objects.filter(runner_team_id=team_id)
        user_stats = Statistic.objects.filter(runner_stat__in=users)

        total_comand_results = user_stats.aggregate(
            total_balls=Sum('total_balls', default=0),
            total_distance=Sum('total_distance', default=0),
            total_time=Sum('total_time', default=timedelta()),
            total_average_temp=Avg('total_average_temp', default=0),
            total_days=Sum('total_days', default=0),
            total_runs=Sum('total_runs', default=0),
            tot_members=Count('runner_stat__username')
        )

        team_total_members = total_comand_results.get('tot_members', 0)

        # Создание записи для команды только если есть участники
        if team_total_members > 0:
            try:
                ComandsResult.objects.create(
                    comand_id=team_id,
                    comands_total_members=team_total_members,
                    comand_total_distance=total_comand_results.get('total_distance', 0),
                    comand_total_balls=total_comand_results.get('total_balls', 0),
                    comand_total_time=format_duration(total_comand_results.get('total_time')),
                    comand_average_temp=total_comand_results.get('total_average_temp', 0),
                    comand_total_runs=total_comand_results.get('total_runs', 0)
                )
            except Exception as e:
                print(e)

    return redirect(reverse('index'))

def recalc_func(request):
    records = RunnerDay.objects.all()

    for record in records:
        recalc_runnerdays(record.id, record.day_distance, record.day_average_temp, record.day_time,
                          record.runner.runner_category)

    return redirect(reverse('index'))


def recalc_runnerdays(rec_id, distance, temp, total_time, category):
    distance_koef = [
        [4.9, 1, 1], [9.9, 1.1, 2.1],
        [14.9, 1.2, 3.3], [19.9, 1.3, 4.6],
        [24.9, 1.4, 6], [29.9, 1.5, 7.5],
        [34.9, 1.6, 9.1], [39.9, 1.7, 10.8],
        [44.9, 1.8, 12.6], [49.9, 1.9, 14.5],
        [50, 2, 16.5]
    ]

    temp_koef = {
        "00:02:38": 2.71,
        "00:02:39": 2.71,
        "00:02:40": 2.71,
        "00:02:41": 2.72,
        "00:02:42": 2.72,
        "00:02:43": 2.72,
        "00:02:44": 2.70,
        "00:02:45": 2.70,
        "00:02:46": 2.70,
        "00:02:47": 2.68,
        "00:02:48": 2.68,
        "00:02:49": 2.68,
        "00:02:50": 2.66,
        "00:02:51": 2.66,
        "00:02:52": 2.66,
        "00:02:53": 2.64,
        "00:02:54": 2.64,
        "00:02:55": 2.64,
        "00:02:56": 2.62,
        "00:02:57": 2.62,
        "00:02:58": 2.62,
        "00:02:59": 2.60,
        "00:03:00": 2.58,
        "00:03:01": 2.58,
        "00:03:02": 2.58,
        "00:03:03": 2.58,
        "00:03:04": 2.58,
        "00:03:05": 2.56,
        "00:03:06": 2.56,
        "00:03:07": 2.56,
        "00:03:08": 2.54,
        "00:03:09": 2.54,
        "00:03:10": 2.54,
        "00:03:11": 2.52,
        "00:03:12": 2.52,
        "00:03:13": 2.52,
        "00:03:14": 2.50,
        "00:03:15": 2.50,
        "00:03:16": 2.50,
        "00:03:17": 2.48,
        "00:03:18": 2.48,
        "00:03:19": 2.48,
        "00:03:20": 2.46,
        "00:03:21": 2.46,
        "00:03:22": 2.46,
        "00:03:23": 2.44,
        "00:03:24": 2.44,
        "00:03:25": 2.44,
        "00:03:26": 2.42,
        "00:03:27": 2.42,
        "00:03:28": 2.42,
        "00:03:29": 2.40,
        "00:03:30": 2.40,
        "00:03:31": 2.40,
        "00:03:32": 2.38,
        "00:03:33": 2.38,
        "00:03:34": 2.38,
        "00:03:35": 2.36,
        "00:03:36": 2.36,
        "00:03:37": 2.36,
        "00:03:38": 2.34,
        "00:03:39": 2.34,
        "00:03:40": 2.34,
        "00:03:41": 2.32,
        "00:03:42": 2.32,
        "00:03:43": 2.30,
        "00:03:45": 2.30,
        "00:03:46": 2.30,
        "00:03:47": 2.28,
        "00:03:48": 2.28,
        "00:03:49": 2.28,
        "00:03:50": 2.26,
        "00:03:51": 2.26,
        "00:03:52": 2.26,
        "00:03:53": 2.24,
        "00:03:54": 2.24,
        "00:03:55": 2.24,
        "00:03:56": 2.22,
        "00:03:57": 2.22,
        "00:03:58": 2.22,
        "00:03:59": 2.20,
        "00:04:00": 2.20,
        "00:04:01": 2.20,
        "00:04:02": 2.18,
        "00:04:03": 2.18,
        "00:04:04": 2.18,
        "00:04:05": 2.16,
        "00:04:06": 2.16,
        "00:04:07": 2.16,
        "00:04:08": 2.14,
        "00:04:09": 2.14,
        "00:04:10": 2.14,
        "00:04:11": 2.12,
        "00:04:12": 2.12,
        "00:04:13": 2.12,
        "00:04:14": 2.10,
        "00:04:15": 2.10,
        "00:04:16": 2.10,
        "00:04:17": 2.08,
        "00:04:18": 2.08,
        "00:04:19": 2.08,
        "00:04:20": 2.06,
        "00:04:21": 2.06,
        "00:04:22": 2.06,
        "00:04:23": 2.04,
        "00:04:24": 2.04,
        "00:04:25": 2.04,
        "00:04:26": 2.02,
        "00:04:27": 2.02,
        "00:04:28": 2.02,
        "00:04:29": 2.0,
        "00:04:30": 1.98,
        "00:04:31": 1.98,
        "00:04:32": 1.98,
        "00:04:33": 1.98,
        "00:04:34": 1.98,
        "00:04:35": 1.96,
        "00:04:36": 1.96,
        "00:04:37": 1.96,
        "00:04:38": 1.94,
        "00:04:39": 1.94,
        "00:04:40": 1.92,
        "00:04:41": 1.92,
        "00:04:42": 1.92,
        "00:04:43": 1.92,
        "00:04:44": 1.90,
        "00:04:45": 1.90,
        "00:04:46": 1.90,
        "00:04:47": 1.88,
        "00:04:48": 1.88,
        "00:04:49": 1.88,
        "00:04:50": 1.86,
        "00:04:51": 1.86,
        "00:04:52": 1.86,
        "00:04:53": 1.84,
        "00:04:54": 1.84,
        "00:04:55": 1.84,
        "00:04:56": 1.82,
        "00:04:57": 1.82,
        "00:04:58": 1.82,
        "00:04:59": 1.80,
        "00:05:00": 1.78,
        "00:05:01": 1.78,
        "00:05:02": 1.78,
        "00:05:03": 1.78,
        "00:05:04": 1.78,
        "00:05:05": 1.76,
        "00:05:06": 1.76,
        "00:05:07": 1.76,
        "00:05:08": 1.74,
        "00:05:09": 1.74,
        "00:05:10": 1.74,
        "00:05:11": 1.72,
        "00:05:12": 1.72,
        "00:05:13": 1.72,
        "00:05:14": 1.70,
        "00:05:15": 1.70,
        "00:05:16": 1.70,
        "00:05:17": 1.68,
        "00:05:18": 1.68,
        "00:05:19": 1.68,
        "00:05:20": 1.66,
        "00:05:21": 1.66,
        "00:05:22": 1.66,
        "00:05:23": 1.64,
        "00:05:24": 1.64,
        "00:05:25": 1.64,
        "00:05:26": 1.62,
        "00:05:27": 1.62,
        "00:05:28": 1.62,
        "00:05:29": 1.60,
        "00:05:30": 1.58,
        "00:05:31": 1.58,
        "00:05:32": 1.58,
        "00:05:33": 1.58,
        "00:05:34": 1.58,
        "00:05:35": 1.56,
        "00:05:36": 1.56,
        "00:05:37": 1.56,
        "00:05:38": 1.54,
        "00:05:39": 1.54,
        "00:05:40": 1.54,
        "00:05:41": 1.52,
        "00:05:42": 1.52,
        "00:05:43": 1.52,
        "00:05:44": 1.50,
        "00:05:45": 1.50,
        "00:05:46": 1.50,
        "00:05:47": 1.48,
        "00:05:48": 1.48,
        "00:05:49": 1.48,
        "00:05:50": 1.46,
        "00:05:51": 1.46,
        "00:05:52": 1.46,
        "00:05:53": 1.44,
        "00:05:54": 1.44,
        "00:05:55": 1.44,
        "00:05:56": 1.42,
        "00:05:57": 1.42,
        "00:05:58": 1.42,
        "00:05:59": 1.40,
        "00:06:00": 1.38,
        "00:06:01": 1.38,
        "00:06:02": 1.38,
        "00:06:03": 1.38,
        "00:06:04": 1.38,
        "00:06:05": 1.36,
        "00:06:06": 1.36,
        "00:06:07": 1.36,
        "00:06:08": 1.34,
        "00:06:09": 1.34,
        "00:06:10": 1.34,
        "00:06:11": 1.32,
        "00:06:12": 1.32,
        "00:06:13": 1.32,
        "00:06:14": 1.30,
        "00:06:15": 1.30,
        "00:06:16": 1.30,
        "00:06:17": 1.28,
        "00:06:18": 1.28,
        "00:06:19": 1.28,
        "00:06:20": 1.26,
        "00:06:21": 1.26,
        "00:06:22": 1.26,
        "00:06:23": 1.24,
        "00:06:24": 1.24,
        "00:06:25": 1.24,
        "00:06:26": 1.22,
        "00:06:27": 1.22,
        "00:06:28": 1.22,
        "00:06:29": 1.20,
        "00:06:30": 1.18,
        "00:06:31": 1.18,
        "00:06:32": 1.18,
        "00:06:33": 1.18,
        "00:06:34": 1.18,
        "00:06:35": 1.16,
        "00:06:36": 1.16,
        "00:06:37": 1.16,
        "00:06:38": 1.14,
        "00:06:39": 1.14,
        "00:06:40": 1.14,
        "00:06:41": 1.12,
        "00:06:42": 1.12,
        "00:06:43": 1.12,
        "00:06:44": 1.10,
        "00:06:45": 1.10,
        "00:06:46": 1.10,
        "00:06:47": 1.08,
        "00:06:48": 1.08,
        "00:06:49": 1.08,
        "00:06:50": 1.06,
        "00:06:51": 1.06,
        "00:06:52": 1.06,
        "00:06:53": 1.04,
        "00:06:54": 1.04,
        "00:06:55": 1.04,
        "00:06:56": 1.02,
        "00:06:57": 1.02,
        "00:06:58": 1.02,
        "00:06:59": 1.0,
        "00:07:00": 0.99,
        "00:07:01": 0.99,
        "00:07:02": 0.99,
        "00:07:03": 0.99,
        "00:07:04": 0.99,
        "00:07:05": 0.98,
        "00:07:06": 0.98,
        "00:07:07": 0.98,
        "00:07:08": 0.97,
        "00:07:09": 0.97,
        "00:07:10": 0.97,
        "00:07:11": 0.96,
        "00:07:12": 0.96,
        "00:07:13": 0.96,
        "00:07:14": 0.95,
        "00:07:15": 0.95,
        "00:07:16": 0.95,
        "00:07:17": 0.94,
        "00:07:18": 0.94,
        "00:07:19": 0.94,
        "00:07:20": 0.93,
        "00:07:21": 0.93,
        "00:07:22": 0.93,
        "00:07:23": 0.92,
        "00:07:24": 0.92,
        "00:07:25": 0.92,
        "00:07:26": 0.91,
        "00:07:27": 0.91,
        "00:07:28": 0.91,
        "00:07:29": 0.90,
        "00:07:30": 0.89,
        "00:07:31": 0.89,
        "00:07:32": 0.89,
        "00:07:33": 0.89,
        "00:07:34": 0.89,
        "00:07:35": 0.88,
        "00:07:36": 0.88,
        "00:07:37": 0.88,
        "00:07:38": 0.87,
        "00:07:39": 0.87,
        "00:07:40": 0.87,
        "00:07:41": 0.86,
        "00:07:42": 0.86,
        "00:07:43": 0.86,
        "00:07:44": 0.85,
        "00:07:45": 0.85,
        "00:07:46": 0.85,
        "00:07:47": 0.84,
        "00:07:48": 0.84,
        "00:07:49": 0.84,
        "00:07:50": 0.83,
        "00:07:51": 0.83,
        "00:07:52": 0.83,
        "00:07:53": 0.82,
        "00:07:54": 0.82,
        "00:07:55": 0.82,
        "00:07:56": 0.81,
        "00:07:57": 0.81,
        "00:07:58": 0.81,
        "00:07:59": 0.80,
        "00:08:00": 0.79,
        "00:08:01": 0.79,
        "00:08:02": 0.79,
        "00:08:03": 0.79,
        "00:08:04": 0.79,
        "00:08:05": 0.78,
        "00:08:06": 0.78,
        "00:08:07": 0.78,
        "00:08:08": 0.77,
        "00:08:09": 0.77,
        "00:08:10": 0.77,
        "00:08:11": 0.76,
        "00:08:12": 0.76,
        "00:08:13": 0.76,
        "00:08:14": 0.75,
        "00:08:15": 0.75,
        "00:08:16": 0.75,
        "00:08:17": 0.74,
        "00:08:18": 0.74,
        "00:08:19": 0.74,
        "00:08:20": 0.73,
        "00:08:21": 0.73,
        "00:08:22": 0.73,
        "00:08:23": 0.72,
        "00:08:24": 0.72,
        "00:08:25": 0.72,
        "00:08:26": 0.71,
        "00:08:27": 0.71,
        "00:08:28": 0.71,
        "00:08:29": 0.70,
        "00:08:30": 0.69,
        "00:08:31": 0.69,
        "00:08:32": 0.69,
        "00:08:33": 0.68,
        "00:08:34": 0.68,
        "00:08:35": 0.68,
        "00:08:36": 0.68,
        "00:08:37": 0.68,
        "00:08:38": 0.67,
        "00:08:39": 0.67,
        "00:08:40": 0.66,
        "00:08:41": 0.66,
        "00:08:42": 0.66,
        "00:08:43": 0.66,
        "00:08:44": 0.65,
        "00:08:45": 0.65,
        "00:08:46": 0.65,
        "00:08:47": 0.64,
        "00:08:48": 0.64,
        "00:08:49": 0.64,
        "00:08:50": 0.63,
        "00:08:51": 0.63,
        "00:08:52": 0.63,
        "00:08:53": 0.62,
        "00:08:54": 0.62,
        "00:08:55": 0.62,
        "00:08:56": 0.61,
        "00:08:57": 0.61,
        "00:08:58": 0.61,
        "00:08:59": 0.60,
        "00:09:00": 0.59,
        "00:09:01": 0.59,
        "00:09:02": 0.59,
        "00:09:05": 0.58,
        "00:09:06": 0.58,
        "00:09:07": 0.58,
        "00:09:08": 0.57,
        "00:09:09": 0.57,
        "00:09:10": 0.57,
        "00:09:11": 0.56,
        "00:09:12": 0.56,
        "00:09:13": 0.56,
        "00:09:14": 0.55,
        "00:09:15": 0.55,
        "00:09:16": 0.55,
        "00:09:17": 0.54,
        "00:09:18": 0.54,
        "00:09:19": 0.54,
        "00:09:20": 0.53,
        "00:09:21": 0.53,
        "00:09:22": 0.53,
        "00:09:23": 0.52,
        "00:09:24": 0.52,
        "00:09:25": 0.52,
        "00:09:26": 0.51,
        "00:09:27": 0.51,
        "00:09:28": 0.51,
        "00:09:29": 0.50,
        "00:09:30": 0.49,
        "00:09:31": 0.49,
        "00:09:32": 0.49,
        "00:09:33": 0.49,
        "00:09:34": 0.49,
        "00:09:35": 0.48,
        "00:09:36": 0.48,
        "00:09:37": 0.48,
        "00:09:38": 0.47,
        "00:09:39": 0.47,
        "00:09:40": 0.47,
        "00:09:41": 0.46,
        "00:09:42": 0.46,
        "00:09:43": 0.46,
        "00:09:44": 0.45,
        "00:09:45": 0.44,
        "00:09:46": 0.44,
        "00:09:47": 0.44,
        "00:09:48": 0.43,
        "00:09:49": 0.43,
        "00:09:50": 0.43,
        "00:09:51": 0.42,
        "00:09:52": 0.42,
        "00:09:53": 0.42,
        "00:09:54": 0.41,
        "00:09:55": 0.41,
        "00:09:56": 0.41,
        "00:09:57": 0.40,
        "00:09:58": 0.40,
        "00:09:59": 0.40,
        "00:10:00": 0.39
    }

    tot_koef = None
    avg_temp_koef = 1
    ball_coef=None
    # if category not in [1, 2]:
    for key in temp_koef:
        if temp.strftime("%H:%M:%S") == key:
            avg_temp_koef = temp_koef[key]
            break

    if not distance or not total_time:
        return '00:00:00', None

    for d in distance_koef:
        if distance <= d[0]:
            if distance < 5:
                need_list_index = 0
            elif 5 <= distance < 10:
                need_list_index = 1
            else:
                need_list_index = distance_koef.index(d) - 1




            if distance >= 5:
                ost_dist = distance - distance_koef[need_list_index][0]
                ost_koef = (distance_koef[need_list_index][1] + 0.1) * ost_dist
                if category not in [1, 2]:
                    tot_koef = ((5 * distance_koef[need_list_index][2] + ost_koef) * avg_temp_koef) * 10

                else:
                    tot_koef = (5 * distance_koef[need_list_index][2] + ost_koef) * 10
                    ball_coef=(5 * distance_koef[need_list_index][2] + ost_koef)*avg_temp_koef * 10
            else:
                ost_koef = distance_koef[need_list_index][1] * distance
                if category not in [1, 2]:
                    tot_koef = (ost_koef * avg_temp_koef) * 10
                else:
                    tot_koef = ost_koef  * 10
                    ball_coef=(ost_koef * avg_temp_koef) * 10


            break
    runnerday = RunnerDay.objects.get(pk=rec_id)
    runnerday.ball = tot_koef
    runnerday.ball_koef = ball_coef
    runnerday.save()

    return




