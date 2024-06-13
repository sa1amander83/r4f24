from datetime import datetime

from asgiref.sync import sync_to_async
from django.db.models import Count, Q, Sum, Avg

from core.models import User, Teams
from profiles.models import Statistic, RunnerDay




class DataMixin:

    # коэф за каждые 5 км

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = User.objects.annotate(Count('runner_category'))
        context['count_of_runners'] = User.objects.all().count() + 1

        context['calend'] = {x: x for x in range(1, 31)}

        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context

    def avg_temp_function(self, user):
        tottime = User.objects.filter(username=user). \
            filter(Q(runner__day_distance__gt=0) & Q(runner__day_average_temp__lte='00:08:00') |
                   Q(runner__day_distance__gt=0) & Q(runner_age__gte=60)).aggregate(Sum('runner__day_average_temp'))

        count = User.objects.filter(username=user). \
            filter(Q(runner__day_distance__gt=0) & Q(runner__day_average_temp__lte='00:08:00') |
                   Q(runner__day_distance__gt=0) & Q(runner_age__gte=60)).count()

        if tottime['runner__day_average_temp__sum'] is None:
            obr = 0
        else:

            obr = (tottime['runner__day_average_temp__sum'] / count)

        def timedelta_tohms(duration):
            if duration != 0:
                days, seconds = duration.days, duration.seconds
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{minutes}:{seconds}"
            else:
                return f"{00}:{00}"

        avg_temp = timedelta_tohms(obr)

        return avg_temp
#ЭТА функция отрабатывает в джаваскрипте
    # def calc_ball(self, dist, avg_time, ):
    #
    #     global need_list, ost_koef, tot_koef
    #     need_list = 0
    #     avg_temp_koef = 0
    #     ost_koef=0
    #     temp_koef={}
    #     distance_koef = [
    #         [4.999, 1, 1], [9.999, 1.1, 2.1],
    #         [14.999, 1.2, 3.3], [19.999, 1.3, 4.6],
    #         [24.999, 1.4, 6], [29.999, 1.5, 7.5],
    #         [34.999, 1.6, 9.1], [39.999, 1.7, 10.8],
    #         [44.999, 1.8, 12.6], [49.999, 1.9, 14.5],
    #         [50, 2, 16.5]
    #     ]
    #
    #     temp_koef = {
    #         "00:02:38": 2.71,
    #         "00:02:41": 2.72,
    #         "00:02:44": 2.70,
    #         "00:02:47": 2.68,
    #         "00:02:50": 2.66,
    #         "00:02:53": 2.64,
    #         "00:02:56": 2.62,
    #         "00:02:59": 2.60,
    #         "00:03:02": 2.58,
    #         "00:03:05": 2.56,
    #         "00:03:08": 2.54,
    #         "00:03:11": 2.52,
    #         "00:03:14": 2.50,
    #         "00:03:17": 2.48,
    #         "00:03:20": 2.46,
    #         "00:03:23": 2.44,
    #         "00:03:26": 2.42,
    #         "00:03:29": 2.40,
    #         "00:03:32": 2.38,
    #         "00:03:35": 2.36,
    #         "00:03:38": 2.34,
    #         "00:03:41": 2.32,
    #         "00:03:44": 2.30,
    #         "00:03:47": 2.28,
    #         "00:03:50": 2.26,
    #         "00:03:53": 2.24,
    #         "00:03:56": 2.22,
    #         "00:03:59": 2.20,
    #         "00:04:02": 2.18,
    #         "00:04:05": 2.16,
    #         "00:04:08": 2.14,
    #         "00:04:11": 2.12,
    #         "00:04:14": 2.10,
    #         "00:04:17": 2.08,
    #         "00:04:20": 2.06,
    #         "00:04:23": 2.04,
    #         "00:04:26": 2.02,
    #         "00:04:29": 2.0,
    #         "00:04:32": 1.98,
    #         "00:04:35": 1.96,
    #         "00:04:38": 1.94,
    #         "00:04:41": 1.92,
    #         "00:04:44": 1.90,
    #         "00:04:47": 1.88,
    #         "00:04:50": 1.86,
    #         "00:04:53": 1.84,
    #         "00:04:56": 1.82,
    #         "00:04:59": 1.80,
    #         "00:05:02": 1.78,
    #         "00:05:05": 1.76,
    #         "00:05:08": 1.74,
    #         "00:05:11": 1.72,
    #         "00:05:14": 1.70,
    #         "00:05:17": 1.68,
    #         "00:05:20": 1.66,
    #         "00:05:23": 1.64,
    #         "00:05:26": 1.62,
    #         "00:05:29": 1.60,
    #         "00:05:32": 1.58,
    #         "00:05:35": 1.56,
    #         "00:05:38": 1.54,
    #         "00:05:41": 1.52,
    #         "00:05:44": 1.50,
    #         "00:05:47": 1.48,
    #         "00:05:50": 1.46,
    #         "00:05:53": 1.44,
    #         "00:05:56": 1.42,
    #         "00:05:59": 1.40,
    #         "00:06:02": 1.38,
    #         "00:06:05": 1.36,
    #         "00:06:08": 1.34,
    #         "00:06:11": 1.32,
    #         "00:06:14": 1.30,
    #         "00:06:17": 1.28,
    #         "00:06:20": 1.26,
    #         "00:06:23": 1.24,
    #         "00:06:26": 1.22,
    #         "00:06:29": 1.20,
    #         "00:06:32": 1.18,
    #         "00:06:35": 1.16,
    #         "00:06:38": 1.14,
    #         "00:06:41": 1.12,
    #         "00:06:44": 1.10,
    #         "00:06:47": 1.08,
    #         "00:06:50": 1.06,
    #         "00:06:53": 1.04,
    #         "00:06:56": 1.02,
    #         "00:06:59": 1.0,
    #         "00:07:02": 0.99,
    #         "00:07:05": 0.98,
    #         "00:07:08": 0.97,
    #         "00:07:11": 0.96,
    #         "00:07:14": 0.95,
    #         "00:07:17": 0.94,
    #         "00:07:20": 0.93,
    #         "00:07:23": 0.92,
    #         "00:07:26": 0.91,
    #         "00:07:29": 0.90,
    #         "00:07:32": 0.89,
    #         "00:07:35": 0.88,
    #         "00:07:38": 0.87,
    #         "00:07:41": 0.86,
    #         "00:07:44": 0.85,
    #         "00:07:47": 0.84,
    #         "00:07:50": 0.83,
    #         "00:07:53": 0.82,
    #         "00:07:56": 0.81,
    #         "00:07:59": 0.80,
    #         "00:08:02": 0.79,
    #         "00:08:05": 0.78,
    #         "00:08:08": 0.77,
    #         "00:08:11": 0.76,
    #         "00:08:14": 0.75,
    #         "00:08:17": 0.74,
    #         "00:08:20": 0.73,
    #         "00:08:23": 0.72,
    #         "00:08:26": 0.71,
    #         "00:08:29": 0.70,
    #         "00:08:32": 0.69,
    #         "00:08:35": 0.68,
    #         "00:08:38": 0.67,
    #         "00:08:41": 0.66,
    #         "00:08:44": 0.65,
    #         "00:08:47": 0.64,
    #         "00:08:50": 0.63,
    #         "00:08:53": 0.62,
    #         "00:08:56": 0.61,
    #         "00:08:59": 0.60,
    #         "00:09:02": 0.59,
    #         "00:09:05": 0.58,
    #         "00:09:08": 0.57,
    #         "00:09:11": 0.56,
    #         "00:09:14": 0.55,
    #         "00:09:17": 0.54,
    #         "00:09:20": 0.53,
    #         "00:09:23": 0.52,
    #         "00:09:26": 0.51,
    #         "00:09:29": 0.50,
    #         "00:09:32": 0.49,
    #         "00:09:35": 0.48,
    #         "00:09:38": 0.47,
    #         "00:09:41": 0.46,
    #         "00:09:44": 0.45,
    #         "00:09:45": 0.44,
    #         "00:09:48": 0.43,
    #         "00:09:51": 0.42,
    #         "00:09:54": 0.41,
    #         "00:09:57": 0.40,
    #         "00:10:00": 0.39
    #     }
    #
    #     for key, val in temp_koef.items():
    #         if str(avg_time) <= key:
    #             avg_temp_koef = val
    #             break
    #
    #     for d in distance_koef:
    #         if dist <= d[0] and dist >=5:
    #
    #             need_list = distance_koef.index(d) - 1
    #             ost_dist = dist - distance_koef[need_list][0]
    #             ost_koef = distance_koef[need_list][1] * ost_dist
    #             tot_koef = (5 * distance_koef[need_list][2] + ost_koef) * avg_temp_koef
    #         else:
    #             need_list=0
    #             ost_koef=dist
    #             tot_koef=dist*distance_koef[need_list][1]
    #
    #
    #     return round(tot_koef)

    def calc_stat(self, runner_id, username):
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
            run_stat_new=Statistic.objects.filter(runner_stat_id=runner_id).update(
                total_distance=dist,
                total_time=':'.join(str(tot_time).split(':')),
                total_average_temp=':'.join(str(avg_time).split(':')),
                total_days=tot_days,
                total_runs=tot_runs,
                total_balls=balls,
                is_qualificated=is_qual
            )


        except:

            run_stat_new=Statistic.objects.create(
                                                total_distance=dist,
                                                total_time=':'.join(str(tot_time).split(':')),
                                                total_average_temp=':'.join(str(avg_time).split(':')),
                                                total_days=tot_days,
                                                total_runs=tot_runs,
                                                total_balls=balls,
                                                is_qualificated=is_qual
                                                )
