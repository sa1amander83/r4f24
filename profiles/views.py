import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, ExpressionWrapper, F, TimeField
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.template.context_processors import csrf, request
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView

from core.models import User
from profiles.models import RunnerDay, Statistic
from profiles.tasks import calc_stat
from profiles.utils import DataMixin
from r4f24.forms import RunnerDayForm


class ProfileUser(LoginRequiredMixin, ListView, DataMixin):
    model = RunnerDay
    template_name = 'profile.html'
    # pk_url_kwarg = 'username'
    slug_url_kwarg = "username"

    # slug_field = "username"

    def get_object(self, queryset=None):
        return self.request.user

    # context_object_name = 'profile'
    # TODO здесь должно быть только отображение  из модели статистики а не расчеты
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(calend='calend')

        # context['calend'] = {x: x for x in range(1, 31)}
        # print(self.kwargs['username'])
        context['runner'] = RunnerDay.objects.filter(runner__username=self.kwargs['username']).order_by(
            'day_select')

        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])
        # print(self.kwargs['username'])

        # result = RunnerDay.objects.filter(runner__username=self.kwargs['username']). \
        #     filter((Q(day_average_temp__lte="00:08:00") & Q(day_distance__gt=0)) |
        #            (Q(day_average_temp__gte='00:08:00') & Q(runner__runner_age__gte=60))).values(
        #     'runner', 'runner__runner_category').annotate(total_dist=Sum('day_distance'),
        #                                                   total_time=Sum('day_time'),
        #                                                   total_average_temp=Sum('day_average_temp'),
        #                                                   day_count=Count(
        #                                                       (Q(day_average_temp__lte="00:08:00") & Q(
        #                                                           day_distance__gt=0)) |
        #                                                       (Q(day_average_temp__gte='00:08:00') & Q(
        #                                                           runner__runner_age__gte=60))),
        #                                                   avg_time=ExpressionWrapper(
        #                                                       F('total_average_temp') / F('day_count'),
        #                                                       output_field=TimeField())). \
        #     order_by('-total_dist')

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0

        # context['user'] = User.objects.filter(username=self.kwargs['username'])
        # print(context['user'])
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

            # avg_temp = timedelta_tohms(obr)
            # # print(avg_temp)
            # context['avg_temp'] = avg_temp
            #
            # context['tot_dist'] = result

            return dict(list(context.items()) + list(c_def.items()))

        else:
            context['data'] = User.objects.filter(username=self.kwargs['username'])
            context['tot_dist'] = {}

            return dict(list(context.items()) + list(c_def.items()))


def start_calculate(user, dist, tot_time, average_time):
    Statistic.objects.update_or_create(
        runner_stat=user,
        total_distance=dist,
        total_time=str(tot_time),
        total_average_temp=str(average_time),
        defaults={
            'runner_stat_id': user.id
        }

    )


class InputRunnerDayData(DataMixin, LoginRequiredMixin, CreateView):
    form_class = RunnerDayForm
    template_name = 'day.html'
    success_url = reverse_lazy('profile:profile')
    # slug_url_kwarg = 'runner'
    # login_url = reverse_lazy('index')
    model = RunnerDay

    # def get_object(self, queryset=None):
    #     return RunnerDay.objects.get(runner_id=id)

    # def get_queryset(self):
    #     return RunnerDay.objects.all()

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        # context['run'] = RunnerDay.objects.filter(runner__user__username=self.kwargs['runner'])

        # context['runner'] = Runner.objects.get(pk=object.id)
        # context['run_id']=RunnerDay.objects.filter(runner_id=self.get_object())

        return context

    # def form_invalid(self, form):
    #     cd = form.cleaned_data
    #     runner__user_username = self.request.user
    #     return redirect('profile', runner=runner__user_username)
    def form_valid(self, form):
        dayselected = form.cleaned_data['day_select']
        count_run_in_day = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_select=dayselected).count()
        args = {}
        args.update(csrf(request))

        # print(count_run_in_day)
        if count_run_in_day <= 1:
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            # print(self.request.user.id)
            userid = User.objects.get(username=self.kwargs['username'])
            # print(userid.id)
            new_item.runner_id = userid.id

            new_item.save()

            total_distance = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(
                Sum('day_distance'))
            dist = total_distance['day_distance__sum']
            total_time = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(Sum('day_time'))
            tot_time = total_time['day_time__sum']
            avg_time = self.avg_temp_function(self.kwargs['username'])


            calc_stat(runner_id=userid.pk,dist=dist,tot_time=tot_time,avg_time=avg_time)

            # try:
            #     run_stat=Statistic.objects.get(runner_stat_id=userid.pk)
            #     run_stat_new = Statistic.objects.filter(runner_stat_id=userid.pk).update(
            #         total_distance=dist,
            #         total_time=':'.join(str(tot_time).split(':')),
            #         total_average_temp=':'.join(str(avg_time).split(':'))
            #     )
            #
            # except:
            #     run_stat = Statistic.objects.create(runner_stat_id=userid.id,
            #                                         total_distance=dist,
            #                                         total_time=':'.join(str(tot_time).split(':')),
            #                                         total_average_temp=':'.join(str(avg_time).split(':')))
            #

                # TODO Запуск таски перерасчета суммарных значений пробега, среднего темпа и времени в модель статистика

            return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request, 'В день учитываются только две пробежки')
            return redirect('profile:profile', username=self.kwargs['username'])

    # def total_dist_function(self, user):
    #     from django.db.models import Sum
    #
    #     total_distance = RunnerDay.objects.filter(runner__username=user).aggregate(Sum('day_distance'))
    #
    #     result = total_distance['day_distance__sum']
    #     Statistic.objects.update_or_create(total_distance=result)
    #     return result
    #
    # def total_time_function(self, user):
    #     from django.db.models import Sum
    #     total_time = RunnerDay.objects.filter(runner__username=user).aggregate(Sum('day_time'))
    #     Statistic.objects.update_or_create(total_time=total_time['day_time__sum'])
    #     return total_time['day_time__sum']

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
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            return f"{minutes}:{seconds}"

        avg_temp = timedelta_tohms(obr)

        # Statistic.objects.get_or_create(sername=user, total_average_temp=avg_temp)
        # return avg_temp
        return obr
