from celery import shared_task
from celery.schedules import crontab
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import CreateError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q, Avg, Count, Window, F, FloatField
from django.db.models.functions import RowNumber
from django.views.decorators.http import require_POST

from core.models import User, ComandsResult, GroupsResult, Teams, Group
from profiles.models import Statistic, Championat, RunnerDay
from r4f24.celery import app
import logging
from datetime import timedelta

# Получаем логгер
logger = logging.getLogger(__name__)


def parse_time(time_str):
    """Преобразует строку времени формата 'HH:MM:SS' в секунды."""
    parts = list(map(int, time_str.split(':')))

    # Добавляем секунды если их нет в строке.
    if len(parts) == 1:  # Если только часы
        h, m, s = parts[0], 0, 0
    elif len(parts) == 2:  # Если часы и минуты
        h, m, s = parts[0], parts[1], 0
    else:
        h, m, s = parts
    return timedelta(hours=h, minutes=m, seconds=s).total_seconds()
def parse_time_delta(time_delta):
    """Преобразует timedelta в секунды."""
    return time_delta.total_seconds()

def format_time(seconds):
    """Преобразует секунды в строку времени формата 'HH:MM:SS'."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

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


    except Exception as e:
        logger.error(f'ошибка пересчета чемпионата: {e}', exc_info=True)
        raise

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def calc_comands(self, username):
    obj = get_user_model().objects.get(username=username)
    try:
        if obj.runner_group is not None:
            group_id = obj.runner_group.id
            users_group = get_user_model().objects.filter(runner_group_id=group_id)
            user_group_stats = Statistic.objects.filter(runner_stat__in=users_group)

            # Агрегация общих результатов группы
            total_group_results = user_group_stats.aggregate(
                total_balls=Sum('total_balls'),
                total_distance=Sum('total_distance'),
                total_time_seconds=Sum('total_time'),
                total_average_temp=Avg('total_average_temp'),
                total_runs=Sum('total_runs'),
                tot_members=Count('runner_stat__username')
            )

            # Извлечение общего времени и преобразование из timedelta
            total_time_td = total_group_results['total_time_seconds'] or timedelta()
            total_time_seconds = parse_time_delta(total_time_td)
            formatted_group_time = format_time(total_time_seconds)

            # Преобразование среднего темпа
            avg_temp_td = total_group_results['total_average_temp'] or timedelta()
            avg_temp_seconds = parse_time_delta(avg_temp_td)
            formatted_group_avg_temp = format_time(avg_temp_seconds)

            GroupsResult.objects.update_or_create(
                group_id=group_id,
                defaults={
                    'group_total_balls': total_group_results.get('total_balls'),
                    'group_total_distance': total_group_results.get('total_distance'),
                    'group_total_time': formatted_group_time,
                    'group_average_temp': formatted_group_avg_temp,
                    'group_total_runs': total_group_results.get('total_runs'),
                    'group_total_members': total_group_results.get('tot_members')
                }
            )
            print('groups done')

        if obj.runner_team:
            team_id = obj.runner_team.id

            users = get_user_model().objects.filter(runner_team_id=team_id)
            user_stats = Statistic.objects.filter(runner_stat__in=users)

            # Агрегация общих результатов команды
            total_comand_results = user_stats.aggregate(
                total_balls=Sum('total_balls'),
                total_distance=Sum('total_distance'),
                total_time_seconds=Sum('total_time'),
                total_average_temp=Avg('total_average_temp'),
                total_runs=Sum('total_runs'),
                tot_members=Count('runner_stat__username')
            )

            # Извлечение и преобразование общего времени команды
            total_time_td = total_comand_results['total_time_seconds'] or timedelta()
            total_time_seconds = parse_time_delta(total_time_td)
            formatted_comand_time = format_time(total_time_seconds)

            # Преобразование среднего темпа команды
            avg_temp_td = total_comand_results['total_average_temp'] or timedelta()
            avg_temp_seconds = parse_time_delta(avg_temp_td)
            formatted_comand_avg_temp = format_time(avg_temp_seconds)

            ComandsResult.objects.update_or_create(
                comand_id=team_id,
                defaults={
                    'comands_total_members': total_comand_results.get('tot_members'),
                    'comand_total_distance': total_comand_results.get('total_distance'),
                    'comand_total_balls': total_comand_results.get('total_balls'),
                    'comand_total_time': formatted_comand_time,
                    'comand_average_temp': formatted_comand_avg_temp,
                    'comand_total_runs': total_comand_results.get('total_runs')
                }
            )
            logger.info('Team results updated successfully.')

    except Exception as e:
        logger.error(f'An error occurred while calculating commands for user {username}: {e}', exc_info=True)
        raise

# @shared_task()




@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def calc_start(self,runner_id, username):
    try:
        runner_days = RunnerDay.objects.filter(runner__username=username)

        # Рассчитываем общую дистанцию
        total_distance = runner_days.aggregate(Sum('day_distance'))['day_distance__sum'] or 0

        # Агрегирование значений времени
        total_time_list = runner_days.values_list('day_time', flat=True)
        total_time_seconds = sum(t.hour * 3600 + t.minute * 60 + t.second for t in total_time_list if t)
        formatted_total_time = format_time(total_time_seconds)

        # Агрегирование средней температуры как времени
        avg_time = runner_days.aggregate(Avg('day_average_temp'))['day_average_temp__avg']
        if avg_time:
            hours, remainder = divmod(avg_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_avg_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            formatted_avg_time = '00:00:00'

        # Подсчитываем количество уникальных пробежек и дней
        total_runs = runner_days.filter(day_distance__gte=0).count()
        total_days = runner_days.filter(day_select__gte=0).distinct('day_select').count()

        # Агрегирование баллов
        tot_balls = runner_days.aggregate(Sum('ball'))['ball__sum'] or 0
        tot_balls_champ = runner_days.aggregate(Sum('ball_for_champ'))['ball_for_champ__sum'] or 0

        # Проверка квалификации
        is_qualified = total_distance >= 50

        # Обновление или создание объекта Statistic
        Statistic.objects.update_or_create(
            runner_stat_id=runner_id,
            defaults={
                'total_distance': total_distance,
                'total_time': formatted_total_time,
                'total_average_temp': formatted_avg_time,
                'total_days': total_days,
                'total_runs': total_runs,
                'total_balls': tot_balls,
                'total_balls_for_champ': tot_balls_champ,
                'is_qualificated': is_qualified
            }
        )
        # calc_comands.delay(username)
    except Exception as e:
        logger.error(f'An error occurred while calculating commands for user {username}: {e}', exc_info=True)
        raise



def calculate_coefficients(runner_day):

    distance_koef = [
        (4.9, 1, 1), (9.9, 1.1, 2.1),
        (14.9, 1.2, 3.3), (19.9, 1.3, 4.6),
        (24.9, 1.4, 6), (29.9, 1.5, 7.5),
        (34.9, 1.6, 9.1), (39.9, 1.7, 10.8),
        (44.9, 1.8, 12.6), (49.9, 1.9, 14.5),
        (50, 2, 16.5)
    ]


    avg_temp_koef = 1
    tot_koef = 0
    ball_for_champ = 0
    temp_koef = {
        "00:02:38": 2.71,"00:02:39": 2.71,        "00:02:40": 2.71,        "00:02:41": 2.72,        "00:02:42": 2.72,
        "00:02:43": 2.72,        "00:02:44": 2.70,        "00:02:45": 2.70,        "00:02:46": 2.70,        "00:02:47": 2.68,
        "00:02:48": 2.68,        "00:02:49": 2.68,        "00:02:50": 2.66,        "00:02:51": 2.66,        "00:02:52": 2.66,
        "00:02:53": 2.64,        "00:02:54": 2.64,        "00:02:55": 2.64,        "00:02:56": 2.62,        "00:02:57": 2.62,
        "00:02:58": 2.62,        "00:02:59": 2.60,        "00:03:00": 2.58,        "00:03:01": 2.58,        "00:03:02": 2.58,
        "00:03:03": 2.58,        "00:03:04": 2.58,        "00:03:05": 2.56,        "00:03:06": 2.56,        "00:03:07": 2.56,
        "00:03:08": 2.54,        "00:03:09": 2.54,        "00:03:10": 2.54,        "00:03:11": 2.52,        "00:03:12": 2.52,
        "00:03:13": 2.52,        "00:03:14": 2.50,        "00:03:15": 2.50,        "00:03:16": 2.50,        "00:03:17": 2.48,
        "00:03:18": 2.48,        "00:03:19": 2.48,        "00:03:20": 2.46,        "00:03:21": 2.46,        "00:03:22": 2.46,
        "00:03:23": 2.44,        "00:03:24": 2.44,        "00:03:25": 2.44,        "00:03:26": 2.42,        "00:03:27": 2.42,
        "00:03:28": 2.42,        "00:03:29": 2.40,        "00:03:30": 2.40,        "00:03:31": 2.40,        "00:03:32": 2.38,
        "00:03:33": 2.38,        "00:03:34": 2.38,        "00:03:35": 2.36,        "00:03:36": 2.36,
        "00:03:37": 2.36,        "00:03:38": 2.34,        "00:03:39": 2.34,        "00:03:40": 2.34,
        "00:03:41": 2.32,        "00:03:42": 2.32,        "00:03:43": 2.30,        "00:03:45": 2.30,
        "00:03:46": 2.30,        "00:03:47": 2.28,        "00:03:48": 2.28,        "00:03:49": 2.28,
        "00:03:50": 2.26,        "00:03:51": 2.26,        "00:03:52": 2.26,        "00:03:53": 2.24,
        "00:03:54": 2.24,        "00:03:55": 2.24,        "00:03:56": 2.22,        "00:03:57": 2.22,
        "00:03:58": 2.22,        "00:03:59": 2.20,        "00:04:00": 2.20,        "00:04:01": 2.20,
        "00:04:02": 2.18,        "00:04:03": 2.18,        "00:04:04": 2.18,        "00:04:05": 2.16,
        "00:04:06": 2.16,        "00:04:07": 2.16,        "00:04:08": 2.14,        "00:04:09": 2.14,
        "00:04:10": 2.14,        "00:04:11": 2.12,        "00:04:12": 2.12,        "00:04:13": 2.12,
        "00:04:14": 2.10,        "00:04:15": 2.10,        "00:04:16": 2.10,        "00:04:17": 2.08,
        "00:04:18": 2.08,        "00:04:19": 2.08,       "00:04:20": 2.06,        "00:04:21": 2.06,
        "00:04:22": 2.06,        "00:04:23": 2.04,        "00:04:24": 2.04,        "00:04:25": 2.04,
        "00:04:26": 2.02,        "00:04:27": 2.02,        "00:04:28": 2.02,        "00:04:29": 2.0,        "00:04:30": 1.98,
        "00:04:31": 1.98,        "00:04:32": 1.98,        "00:04:33": 1.98,
        "00:04:34": 1.98,        "00:04:35": 1.96,        "00:04:36": 1.96,        "00:04:37": 1.96,
        "00:04:38": 1.94,        "00:04:39": 1.94,        "00:04:40": 1.92,        "00:04:41": 1.92,
        "00:04:42": 1.92,        "00:04:43": 1.92,       "00:04:44": 1.90,        "00:04:45": 1.90,
        "00:04:46": 1.90,        "00:04:47": 1.88,        "00:04:48": 1.88,        "00:04:49": 1.88,
        "00:04:50": 1.86,        "00:04:51": 1.86,        "00:04:52": 1.86,        "00:04:53": 1.84,
        "00:04:54": 1.84,        "00:04:55": 1.84,        "00:04:56": 1.82,        "00:04:57": 1.82,
        "00:04:58": 1.82,        "00:04:59": 1.80,        "00:05:00": 1.78,        "00:05:01": 1.78,
        "00:05:02": 1.78,        "00:05:03": 1.78,        "00:05:04": 1.78,        "00:05:05": 1.76,
        "00:05:06": 1.76,        "00:05:07": 1.76,        "00:05:08": 1.74,        "00:05:09": 1.74,
        "00:05:10": 1.74,        "00:05:11": 1.72,        "00:05:12": 1.72,        "00:05:13": 1.72,
        "00:05:14": 1.70,        "00:05:15": 1.70,        "00:05:16": 1.70,        "00:05:17": 1.68,
        "00:05:18": 1.68,        "00:05:19": 1.68,        "00:05:20": 1.66,        "00:05:21": 1.66,        "00:05:22": 1.66,        "00:05:23": 1.64,
        "00:05:24": 1.64,        "00:05:25": 1.64,        "00:05:26": 1.62,        "00:05:27": 1.62,
        "00:05:28": 1.62,        "00:05:29": 1.60,        "00:05:30": 1.58,        "00:05:31": 1.58,
        "00:05:32": 1.58,        "00:05:33": 1.58,        "00:05:34": 1.58,       "00:05:35": 1.56,
        "00:05:36": 1.56,        "00:05:37": 1.56,        "00:05:38": 1.54,        "00:05:39": 1.54,
        "00:05:40": 1.54,        "00:05:41": 1.52,        "00:05:42": 1.52,        "00:05:43": 1.52,
        "00:05:44": 1.50,        "00:05:45": 1.50,        "00:05:46": 1.50,        "00:05:47": 1.48,
        "00:05:48": 1.48,        "00:05:49": 1.48,        "00:05:50": 1.46,        "00:05:51": 1.46,
        "00:05:52": 1.46,        "00:05:53": 1.44,        "00:05:54": 1.44,        "00:05:55": 1.44,
        "00:05:56": 1.42,        "00:05:57": 1.42,        "00:05:58": 1.42,        "00:05:59": 1.40,
        "00:06:00": 1.38,        "00:06:01": 1.38,        "00:06:02": 1.38,        "00:06:03": 1.38,
        "00:06:04": 1.38,        "00:06:05": 1.36,        "00:06:06": 1.36,        "00:06:07": 1.36,
        "00:06:08": 1.34,        "00:06:09": 1.34,        "00:06:10": 1.34,        "00:06:11": 1.32,
        "00:06:12": 1.32,        "00:06:13": 1.32,        "00:06:14": 1.30,
        "00:06:15": 1.30,        "00:06:16": 1.30,        "00:06:17": 1.28,        "00:06:18": 1.28,
        "00:06:19": 1.28,        "00:06:20": 1.26,        "00:06:21": 1.26,        "00:06:22": 1.26,
        "00:06:23": 1.24,        "00:06:24": 1.24,        "00:06:25": 1.24,        "00:06:26": 1.22,
        "00:06:27": 1.22,        "00:06:28": 1.22,        "00:06:29": 1.20,        "00:06:30": 1.18,
        "00:06:31": 1.18,        "00:06:32": 1.18,        "00:06:33": 1.18,        "00:06:34": 1.18,
        "00:06:35": 1.16,        "00:06:36": 1.16,        "00:06:37": 1.16,        "00:06:38": 1.14,
        "00:06:39": 1.14,        "00:06:40": 1.14,       "00:06:41": 1.12,
        "00:06:42": 1.12,        "00:06:43": 1.12,        "00:06:44": 1.10,        "00:06:45": 1.10,
        "00:06:46": 1.10,        "00:06:47": 1.08,        "00:06:48": 1.08,        "00:06:49": 1.08,
        "00:06:50": 1.06,        "00:06:51": 1.06,        "00:06:52": 1.06,        "00:06:53": 1.04,
        "00:06:54": 1.04,        "00:06:55": 1.04,        "00:06:56": 1.02,        "00:06:57": 1.02,
        "00:06:58": 1.02,        "00:06:59": 1.0,        "00:07:00": 0.99,       "00:07:01": 0.99,
        "00:07:02": 0.99,        "00:07:03": 0.99,        "00:07:04": 0.99,
        "00:07:05": 0.98,        "00:07:06": 0.98,        "00:07:07": 0.98,        "00:07:08": 0.97,
        "00:07:09": 0.97,        "00:07:10": 0.97,        "00:07:11": 0.96,        "00:07:12": 0.96,
        "00:07:13": 0.96,        "00:07:14": 0.95,        "00:07:15": 0.95,        "00:07:16": 0.95,        "00:07:17": 0.94,
        "00:07:18": 0.94,        "00:07:19": 0.94,        "00:07:20": 0.93,       "00:07:21": 0.93,
        "00:07:22": 0.93,        "00:07:23": 0.92,        "00:07:24": 0.92,        "00:07:25": 0.92,
        "00:07:26": 0.91,        "00:07:27": 0.91,        "00:07:28": 0.91,        "00:07:29": 0.90,
        "00:07:30": 0.89,        "00:07:31": 0.89,       "00:07:32": 0.89,       "00:07:33": 0.89,
        "00:07:34": 0.89,        "00:07:35": 0.88,        "00:07:36": 0.88,
        "00:07:37": 0.88,      "00:07:38": 0.87,        "00:07:39": 0.87,        "00:07:40": 0.87,
        "00:07:41": 0.86,        "00:07:42": 0.86,        "00:07:43": 0.86,        "00:07:44": 0.85,        "00:07:45": 0.85,
        "00:07:46": 0.85,        "00:07:47": 0.84,        "00:07:48": 0.84,        "00:07:49": 0.84,
        "00:07:50": 0.83,        "00:07:51": 0.83,        "00:07:52": 0.83,        "00:07:53": 0.82,
        "00:07:54": 0.82,        "00:07:55": 0.82,        "00:07:56": 0.81,        "00:07:57": 0.81,
        "00:07:58": 0.81,        "00:07:59": 0.80,        "00:08:00": 0.79,        "00:08:01": 0.79,
        "00:08:02": 0.79,        "00:08:03": 0.79,        "00:08:04": 0.79,
        "00:08:05": 0.78,        "00:08:06": 0.78,        "00:08:07": 0.78,        "00:08:08": 0.77,
        "00:08:09": 0.77,        "00:08:10": 0.77,        "00:08:11": 0.76,        "00:08:12": 0.76,
        "00:08:13": 0.76,        "00:08:14": 0.75,        "00:08:15": 0.75,        "00:08:16": 0.75,
        "00:08:17": 0.74,        "00:08:18": 0.74,        "00:08:19": 0.74,        "00:08:20": 0.73,
        "00:08:21": 0.73,        "00:08:22": 0.73,        "00:08:23": 0.72,        "00:08:24": 0.72,
        "00:08:25": 0.72,        "00:08:26": 0.71,        "00:08:27": 0.71,        "00:08:28": 0.71,
        "00:08:29": 0.70,        "00:08:30": 0.69,        "00:08:31": 0.69,
        "00:08:32": 0.69,        "00:08:33": 0.68,        "00:08:34": 0.68,        "00:08:35": 0.68,
        "00:08:36": 0.68,        "00:08:37": 0.68,       "00:08:38": 0.67,        "00:08:39": 0.67,
        "00:08:40": 0.66,        "00:08:41": 0.66,        "00:08:42": 0.66,
        "00:08:43": 0.66,        "00:08:44": 0.65,        "00:08:45": 0.65,
        "00:08:46": 0.65,        "00:08:47": 0.64,        "00:08:48": 0.64,
        "00:08:49": 0.64,       "00:08:50": 0.63,        "00:08:51": 0.63,        "00:08:52": 0.63,
        "00:08:53": 0.62,        "00:08:54": 0.62,        "00:08:55": 0.62,        "00:08:56": 0.61,
        "00:08:57": 0.61,        "00:08:58": 0.61,        "00:08:59": 0.60,
        "00:09:00": 0.59,        "00:09:01": 0.59,        "00:09:02": 0.59,        "00:09:05": 0.58,
        "00:09:06": 0.58,        "00:09:07": 0.58,        "00:09:08": 0.57,       "00:09:09": 0.57,
        "00:09:10": 0.57,        "00:09:11": 0.56,        "00:09:12": 0.56,        "00:09:13": 0.56,
        "00:09:14": 0.55,        "00:09:15": 0.55,        "00:09:16": 0.55,
        "00:09:17": 0.54,        "00:09:18": 0.54,        "00:09:19": 0.54,        "00:09:20": 0.53,
        "00:09:21": 0.53,        "00:09:22": 0.53,        "00:09:23": 0.52,        "00:09:24": 0.52,
        "00:09:25": 0.52,        "00:09:26": 0.51,        "00:09:27": 0.51,        "00:09:28": 0.51,
        "00:09:29": 0.50,        "00:09:30": 0.49,        "00:09:31": 0.49,        "00:09:32": 0.49,
        "00:09:33": 0.49,        "00:09:34": 0.49,      "00:09:35": 0.48,
        "00:09:36": 0.48,        "00:09:37": 0.48,        "00:09:38": 0.47,
        "00:09:39": 0.47,        "00:09:40": 0.47,        "00:09:41": 0.46,        "00:09:42": 0.46,
        "00:09:43": 0.46,        "00:09:44": 0.45,        "00:09:45": 0.44,        "00:09:46": 0.44,
        "00:09:47": 0.44,       "00:09:48": 0.43,       "00:09:49": 0.43,        "00:09:50": 0.43,
        "00:09:51": 0.42,        "00:09:52": 0.42,
        "00:09:53": 0.42,        "00:09:54": 0.41,        "00:09:55": 0.41,        "00:09:56": 0.41,
        "00:09:57": 0.40,        "00:09:58": 0.40,        "00:09:59": 0.40,        "00:10:00": 0.39
    }


    distance=runner_day.day_distance
    # total_time=runner_day.day_time
    temp=runner_day.day_average_temp

    # hours, minutes, seconds = temp
    formatted_temp =  temp.strftime("%H:%M:%S")

    #
    # if distance is None or total_time is None:
    #     return tot_koef, ball_for_champ, "Ошибка: Проверьте входные данные"


    for d in distance_koef:
        if distance <= d[0]:
            if distance < 5:
                ost_dist = distance
                ost_koef = distance_koef[0][1] * ost_dist
                num = distance_koef[0][2]
            else:
                index = max(1, int(distance / 5))
                ost_dist = distance - (distance_koef[index-1][0] + 0.1)
                ost_koef = distance_koef[index][1] * ost_dist
                num = distance_koef[index-1][2]

            if formatted_temp in temp_koef:
                avg_temp_koef = temp_koef[formatted_temp]

            if distance >= 5:
                tot_koef = round((5 * num + ost_koef) * 10)
                ball_for_champ = round(((5 * num + ost_koef) * avg_temp_koef) * 10)
            else:
                tot_koef = ost_koef * 10
                ball_for_champ = ost_koef * avg_temp_koef * 10

            break



    return tot_koef, ball_for_champ

@require_POST
def recalculate_balls(request):
    runner_days = RunnerDay.objects.all()


    for runner_day in runner_days:
        user_id = runner_day.runner.id
        username = runner_day.runner.username
        new_balls, new_balls_for_champ = calculate_coefficients(runner_day)
        runner_day.ball = new_balls
        runner_day.ball_for_champ = new_balls_for_champ
        runner_day.save()



    stats=Statistic.objects.all()
    for stat in stats:
        user_id = stat.runner_stat.id
        username = stat.runner_stat.username

        calc_start.delay(user_id, username)

    from django.shortcuts import redirect
    return redirect('index')
