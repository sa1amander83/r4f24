from django.db.models import Count, Q, Sum

from core.models import User
from profiles.models import Statistic, RunnerDay


class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = User.objects.annotate(Count('runner_category'))
        context['count_of_runners'] = User.objects.all().count() + 1

        context['calend'] = {x: x for x in range(1, 31)}

        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context

    def calc_stat(self, runner_id, dist, tot_time, avg_time, tot_days, tot_runs):
        try:
            run_stat = Statistic.objects.get(runner_stat_id=runner_id)
            run_stat_new = Statistic.objects.filter(runner_stat_id=runner_id).update(
                total_distance=dist,
                total_time=':'.join(str(tot_time).split(':')),
                total_average_temp=':'.join(str(avg_time).split(':')),
                total_days=tot_days,
                total_runs=tot_runs
            )

        except:
            run_stat = Statistic.objects.create(runner_stat_id=runner_id,
                                                total_distance=dist,
                                                total_time=':'.join(str(tot_time).split(':')),
                                                total_average_temp=':'.join(str(avg_time).split(':')),
                                                total_days=tot_days,
                                                total_runs=tot_runs)

    def avg_temp_function(self, user):
        tottime = User.objects.filter(username=user). \
            filter(Q(runner__day_distance__gt=0) & Q(runner__day_average_temp__lte='00:08:00') |
                   Q(runner__day_distance__gt=0) & Q(runner_age__gte=60)).aggregate(Sum('runner__day_average_temp'))

        count = User.objects.filter(username=user). \
            filter(Q(runner__day_distance__gt=0) & Q(runner__day_average_temp__lte='00:08:00') |
                   Q(runner__day_distance__gt=0) & Q(runner_age__gte=60)).count()

        obr = (tottime['runner__day_average_temp__sum'] / count)

        def timedelta_tohms(duration):
            days, seconds = duration.days, duration.seconds

            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{minutes}:{seconds}"

        avg_temp = timedelta_tohms(obr)

        return avg_temp
