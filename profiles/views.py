import os

from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.deletion import Collector
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from django.template.context_processors import csrf, request
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from tornado.gen import Runner

from core.models import User, Family
from profiles.models import RunnerDay, Statistic, Photo
from profiles.tasks import get_best_five_summ, calc_stat

from profiles.utils import DataMixin
from r4f24.forms import RunnerDayForm, AddFamilyForm, RegisterUserForm


class ProfileUser(LoginRequiredMixin, ListView, DataMixin):
    model = RunnerDay
    template_name = 'profile.html'

    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(calend='calend')
        context['user_data'] = User.objects.filter(username=self.kwargs['username'])

        context['run_user'] = User.objects.get(username=self.kwargs['username'])

        # photo = run_user.photos.filter(day_select=)

        context['runner_day'] = RunnerDay.objects.filter(runner__username=self.kwargs['username']).order_by(
            'day_select')

        photos = User.objects.get(username=self.kwargs['username'])
        context['images'] = photos.photos.all()

        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])
        context['runner_stat'] = self.kwargs['username']

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0

        obj = RunnerDay.objects.filter(runner__username=self.kwargs['username'])

        if len(obj) > 0:

            return dict(list(context.items()) + list(c_def.items()))

        else:
            context['user_data'] = User.objects.filter(username=self.kwargs['username'])
            context['tot_dist'] = {}

            return dict(list(context.items()) + list(c_def.items()))


class EditProfile(LoginRequiredMixin, UpdateView, DataMixin):
    model = User
    template_name = 'editprofile.html'

    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.object})

    def get_object(self, queryset=None):
        return self.request.user

    fields = ['runner_age', 'runner_category', 'runner_gender', 'zabeg22', 'zabeg23']


class InputRunnerDayData(DataMixin, LoginRequiredMixin, CreateView):
    form_class = RunnerDayForm
    template_name = 'day.html'
    success_url = reverse_lazy('profile:profile')
    model = RunnerDay

    def form_valid(self, form):

        dayselected = form.cleaned_data['day_select']
        count_run_in_day = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_select=dayselected).count()

        if count_run_in_day <= 1:
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            userid = User.objects.get(username=self.kwargs['username'])
            new_item.runner_id = userid.id

            new_item.save()

            for each in form.cleaned_data['photo']:
                Photo.objects.create(runner_id=userid.id,
                                     number_of_run=form.cleaned_data['number_of_run'],
                                     day_select=dayselected,
                                     photo=each)
            # calc_stat.delay(
            #     runner_id=new_item.runner.id,
            #     username=new_item.runner.username
            #     # dist=new_item.day_distance,
            #     # tot_time=new_item.day_time,
            #     # avg_time=new_item.day_average_temp,
            #     # tot_days=new_item.total_days,
            #     # tot_runs=new_item.total_runs
            # )
            print(self.request.user.pk,self.kwargs['username'])

            calc_stat.delay(runner_id=self.request.user.pk, username=self.kwargs['username'])

            return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request,
                           'В день учитываются только две пробежки, обновите сведения по одной из пробежек')
            calc_stat.delay(runner_id=self.request.user.pk, username=self.kwargs['username'])
            # get_best_five_summ.delay()
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
        dayselected = form.cleaned_data['day_select']

        new_item.save()

        old_image = Photo.objects.filter(day_select=dayselected).filter(
            number_of_run=form.cleaned_data['number_of_run'])

        for im in old_image:
            Photo.objects.get(pk=im.pk).delete()
            if os.path.exists(im.photo.path):
                os.remove(im.photo.path)

        for each in form.cleaned_data['photo']:
            Photo.objects.create(runner_id=userid.id,
                                 day_select=dayselected,
                                 number_of_run=form.cleaned_data['number_of_run'],
                                 photo=each)

        # calc_stat.delay(
        #     runner_id=new_item.runner.id,
        #     username=new_item.runner.username
        #     # dist=new_item.day_distance,
        #     # tot_time=new_item.day_time,
        #     # avg_time=new_item.day_average_temp,
        #     # tot_days=new_item.total_days,
        #     # tot_runs=new_item.total_runs
        # )
        # get_best_five_summ.delay()
        return redirect('profile:profile', username=self.request.user)


# class DeleteRunnerDayData(DeleteView):
#     model = RunnerDay
#     template_name = 'deleteday.html'
#     context_object_name = 'runday'
#
#     def get_success_url(self):
#         return  reverse_lazy('profile:profile', kwargs={'username': self.request.user.username})
#
#
#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         runner_id = self.object.runner.id
#         day_distance = self.object.day_distance
#         day_time = self.object.day_time
#         day_average_temp = self.object.day_average_temp
#         total_days = self.object.total_days
#         total_runs = self.object.total_runs
#
#         get_runday = self.object.day_select
#         get_number_run = self.object.number_of_run
#
#         # Delete the RunnerDay instance
#         self.object.delete()
#
#         # Delete associated photos
#         photos = Photo.objects.filter(runner__username=self.kwargs['username'])
#         old_image = Photo.objects.filter(day_select=get_runday).filter(number_of_run=get_number_run)
#
#         for im in old_image:
#             if os.path.exists(im.photo.path):
#                 os.remove(im.photo.path)
#             im.delete()
#
#         # Call the calc_stat task
#         calc_stat.delay(
#             runner_id=runner_id,
#             dist=day_distance,
#             tot_time=day_time,
#             avg_time=day_average_temp,
#             tot_days=total_days,
#             tot_runs=total_runs
#         )
#
#         success_url = reverse_lazy('profile:profile', kwargs={'username': self.request.user.username})
#         return redirect(success_url)
#


class DeleteRunnerDayData(DeleteView, DataMixin):
    model = RunnerDay
    template_name = 'deleteday.html'

    context_object_name = 'runday'

    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.object.runner})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        us=self.object.username
        print(us)

        # get_runday = RunnerDay.objects.get(pk=self.kwargs['pk']).day_select
        # get_number_run = RunnerDay.objects.get(pk=self.kwargs['pk']).number_of_run

        self.object.delete()
        photos = Photo.objects.filter(runner__username=self.kwargs['username'])
        old_image = Photo.objects.filter(day_select=self.object.day_select).filter(
            number_of_run=self.object.number_of_run)

        for im in old_image:
            Photo.objects.get(pk=im.pk).delete()
            if os.path.exists(im.photo.path):
                os.remove(im.photo.path)
        print(self.object.username)
        # success_url = reverse_lazy('profile:profile', kwargs={'username': self.object.user})
        success_msg = 'Запись удалена!'
        # total_distance = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(
        #     Sum('day_distance'))
        # if total_distance['day_distance__sum'] is None:
        #     dist = 0
        # else:
        #     dist = total_distance['day_distance__sum']
        #
        # total_time = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(Sum('day_time'))
        # if total_time['day_time__sum'] is None:
        #     tot_time = '00:00'
        # else:
        #     tot_time = total_time['day_time__sum']
        # avg_time = self.avg_temp_function(self.kwargs['username'])
        #
        # tot_runs = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
        #     day_distance__gt=0).count()
        # tot_days = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
        #     day_select__gt=0).distinct('day_select').count()
        #
        # tot_balls = RunnerDay.objects.filter(runner__username=self.kwargs['username']).aggregate(Sum('ball'))
        # if tot_balls['ball__sum'] is None:
        #     balls = 0
        # else:
        #     balls = tot_balls['ball__sum']

        calc_stat.delay(
            runner_id=self.object.runner.id,
            username=self.object.runner.username
        )
        # get_best_five_summ.delay()
        # return redirect(success_url, success_msg)


#

class AddFamily(CreateView, LoginRequiredMixin):
    model = Family
    template_name = 'addfamily.html'
    form_class = AddFamilyForm
    success_url = reverse_lazy('profile:profile')

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
