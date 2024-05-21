import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, ExpressionWrapper, F, TimeField
from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView, ListView

from core.models import User
from profiles.models import RunnerDay
from profiles.utils import DataMixin


class ProfileUser( ListView, DataMixin):
    model = RunnerDay
    template_name = 'profile.html'
    pk_url_kwarg='username'
    slug_url_kwarg = "runner"
    slug_field = "runner"

    def user(self):
        return RunnerDay.objects.get(pk=self.pk)

    context_object_name = 'profile'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(calend='calend')

        # context['calend'] = {x: x for x in range(1, 31)}

        context['runner'] = RunnerDay.objects.filter(runner__username=self.kwargs['username']).order_by(
            'day_select')
        # print(context['runner'])

        result = RunnerDay.objects.filter(runner__username=self.kwargs['username']). \
            filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
                   (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
            'runner__username', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
                                                                          total_time=Sum('day_time'),
                                                                          total_average_temp=Sum('day_average_temp'),
                                                                          day_count=Count(
                                                                              (Q(day_average_temp__lte="00:08:00") & Q(
                                                                                  day_distance__gt=0)) |
                                                                              (Q(day_average_temp__gte='00:08:00') & Q(
                                                                                  runner__runner_age__gte=60))),
                                                                          avg_time=ExpressionWrapper(
                                                                              F('total_average_temp') / F('day_count'),
                                                                              output_field=TimeField())). \
            order_by('-total_dist')

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0

        context['data'] = User.objects.filter(username=self.kwargs['username'])
        obj = RunnerDay.objects.filter(runner__username=self.kwargs['username'])
        if len(obj) > 0:
            tottime = User.objects.filter(username=self.kwargs['username']). \
                filter(Q(runner__day_distance__gt=0) & Q(runner__day_average_temp__lte='00:08:00') |
                       Q(runner__day_distance__gt=0) & Q(runner_age__gte=60)).aggregate(Sum('runner__day_average_temp'))

            count = User.objects.filter(username=self.kwargs['username']). \
                filter(Q(runner__day_distance__gt=0) & Q(runner__day_average_temp__lte='00:08:00') |
                       Q(runner__day_distance__gt=0) & Q(runner_age__gte=60)).count()

            if tottime != 0 and count > 0:
                obr = tottime['runner__day_average_temp__sum'] / count
            else:
                obr = datetime.timedelta(0)

            def timedelta_tohms(duration):
                days, seconds = duration.days, duration.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{minutes}:{seconds}"

            avg_temp = timedelta_tohms(obr)
            # print(avg_temp)
            context['avg_temp'] = avg_temp

            context['tot_dist'] = result

            return dict(list(context.items()) + list(c_def.items()))

        else:
            context['data'] = User.objects.filter(username=self.kwargs['username'])
            context['tot_dist'] = {}

            return dict(list(context.items()) + list(c_def.items()))