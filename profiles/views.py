
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect

from django.template.context_processors import csrf, request
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from core.models import User
from profiles.models import RunnerDay, Statistic

from profiles.utils import DataMixin
from r4f24.forms import RunnerDayForm


class ProfileUser(LoginRequiredMixin, ListView, DataMixin):
    model = RunnerDay
    template_name = 'profile.html'

    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return self.request.user

    # TODO здесь должно быть только отображение  из модели статистики а не расчеты
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(calend='calend')

        context['runner_day'] = RunnerDay.objects.filter(runner__username=self.kwargs['username']).order_by(
            'day_select')

        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0

        obj = RunnerDay.objects.filter(runner__username=self.kwargs['username'])

        if len(obj) > 0:

            return dict(list(context.items()) + list(c_def.items()))

        else:
            context['data'] = User.objects.filter(username=self.kwargs['username'])
            context['tot_dist'] = {}

            return dict(list(context.items()) + list(c_def.items()))


class InputRunnerDayData(DataMixin, LoginRequiredMixin, CreateView):
    form_class = RunnerDayForm
    template_name = 'day.html'
    success_url = reverse_lazy('profile:profile')
    model = RunnerDay

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def form_valid(self, form):
        dayselected = form.cleaned_data['day_select']
        count_run_in_day = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_select=dayselected).count()
        args = {}
        args.update(csrf(request))

        if count_run_in_day <= 1:
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            userid = User.objects.get(username=self.kwargs['username'])
            new_item.runner_id = userid.id
            new_item.save()

            total_distance = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(
                Sum('day_distance'))
            dist = total_distance['day_distance__sum']
            total_time = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(Sum('day_time'))
            tot_time = total_time['day_time__sum']
            avg_time = self.avg_temp_function(self.kwargs['username'])

            tot_runs = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
                day_distance__gt=0).count()
            tot_days = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
                day_select__gte=0).distinct('day_select').count()

            self.calc_stat(runner_id=self.request.user.pk, dist=dist, tot_time=tot_time, avg_time=avg_time,
                           tot_days=tot_days,
                           tot_runs=tot_runs)

            return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request, 'В день учитываются только две пробежки')
            return redirect('profile:profile', username=self.kwargs['username'])


class EditRunnerDayData(LoginRequiredMixin, UpdateView, DataMixin):
    form_class = RunnerDayForm
    model = RunnerDay
    template_name = 'day.html'

    slug_url_kwarg = 'runner'

    login_url = reverse_lazy('index')

    def get_queryset(self):
        return RunnerDay.objects.all()

    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'runner': self.object})

    def form_valid(self, form):
        cd = form.cleaned_data
        new_item = form.save(commit=False)
        userid = User.objects.get(id=self.request.user.id)

        new_item.runner_id = userid.id

        new_item.save()

        total_distance = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(
            Sum('day_distance'))
        dist = total_distance['day_distance__sum']
        total_time = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(Sum('day_time'))
        tot_time = total_time['day_time__sum']
        avg_time = self.avg_temp_function(self.kwargs['username'])

        tot_runs = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_distance__gt=0).count()
        tot_days = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_select__gt=0).distinct('day_select').count()

        self.calc_stat(runner_id=self.request.user.pk, dist=dist, tot_time=tot_time, avg_time=avg_time,
                       tot_days=tot_days,
                       tot_runs=tot_runs)

        return redirect('profile:profile', username=self.request.user)


class DeleteRunnerDayData(DeleteView, DataMixin):
    model = RunnerDay
    template_name = 'deleteday.html'

    context_object_name = 'runday'

    def form_valid(self, form):
        self.object.delete()

        success_url = reverse_lazy('profile:profile', kwargs={'username': self.request.user})
        success_msg = 'Запись удалена!'
        total_distance = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(
            Sum('day_distance'))
        dist = total_distance['day_distance__sum']
        total_time = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(Sum('day_time'))
        tot_time = total_time['day_time__sum']
        avg_time = self.avg_temp_function(self.kwargs['username'])

        tot_runs = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_distance__gt=0).count()
        tot_days = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_select__gt=0).distinct('day_select').count()

        self.calc_stat(runner_id=self.request.user.pk, dist=dist, tot_time=tot_time, avg_time=avg_time,
                       tot_days=tot_days,
                       tot_runs=tot_runs)

        return redirect(success_url, success_msg)
