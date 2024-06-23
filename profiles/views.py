import os

from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import redirect, render, get_object_or_404

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from core.models import User, Group, Teams
from profiles.models import RunnerDay, Statistic, Photo
from profiles.tasks import get_best_five_summ,  calc_start

from profiles.utils import DataMixin
from r4f24.forms import RunnerDayForm, AddFamilyForm,  FamilyForm, ResetForm


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
            'day_select', 'number_of_run')

        photos = User.objects.get(username=self.kwargs['username'])
        context['images'] = photos.photos.all()

        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])
        context['runner_stat'] = self.kwargs['username']

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0

        obj = RunnerDay.objects.filter(runner__username=self.kwargs['username'])


        context['runner_status']=User.objects.filter(runner_status__gt=0)
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
        first_run = RunnerDay.objects.filter(runner__username=self.kwargs['username']).filter(
            day_select=dayselected).filter(number_of_run=1).count()


        if first_run <= 1:
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            userid = User.objects.get(username=self.kwargs['username'])
            new_item.runner_id = userid.id
            number_of_run = 2 if first_run == 1 else 1
            for each in form.cleaned_data['photo']:
                runner_id = userid.id
                dayselected = dayselected

                filename = each.name
                filepath = os.path.join('media', str(userid.username), str(dayselected), str(number_of_run), filename)

                Photo.objects.create(runner_id=runner_id,
                                     number_of_run=number_of_run,
                                     day_select=dayselected,
                                     photo=each)

            RunnerDay.objects.create(
                runner_id=userid.id,
                day_select=form.cleaned_data['day_select'],
                day_distance=form.cleaned_data['day_distance'],
                day_time=form.cleaned_data['day_time'],
                day_average_temp=form.cleaned_data['day_average_temp'],
                ball=form.cleaned_data['ball'],
                number_of_run=number_of_run

            )



            calc_start.delay(self.request.user.pk, self.kwargs['username'])
            get_best_five_summ.delay()
            return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request, 'В день учитываются только две пробежки, обновите сведения по одной из пробежек')
            # calc_stat(runner_id=self.request.user.pk, username=self.kwargs['username'])
            get_best_five_summ.delay()
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
        self.object=self.get_object()
        cd = form.cleaned_data
        new_item = form.save(commit=False)
        userid = User.objects.get(id=self.request.user.id)

        new_item.runner_id = userid.id
        dayselected = self.object.day_select
        runs = self.object.number_of_run

        old_image = Photo.objects.filter(day_select=dayselected).filter(
            number_of_run=runs)

        for im in old_image:
            Photo.objects.get(pk=im.pk).delete()
            if os.path.exists(im.photo.path):
                os.remove(im.photo.path)

        for each in form.cleaned_data['photo']:
            Photo.objects.create(runner_id=userid.id,
                                 day_select=dayselected,
                                 number_of_run=runs,
                                 photo=each)


        new_item.save()




        calc_start.delay(self.request.user.pk, self.kwargs['username'])
        get_best_five_summ.delay()
        return redirect('profile:profile', username=self.request.user)


class DeleteRunnerDayData(DeleteView, DataMixin):
    model = RunnerDay
    template_name = 'deleteday.html'

    context_object_name = 'runday'

    def form_valid(self, form):
        self.object=self.get_object()
        get_runday = RunnerDay.objects.get(pk=self.kwargs['pk']).day_select
        get_number_run = self.object.number_of_run
        self.object.delete()
        photos = Photo.objects.filter(runner__username=self.kwargs['username'])
        old_image = Photo.objects.filter(day_select=get_runday).filter(number_of_run=get_number_run)

        for im in old_image:
            Photo.objects.get(pk=im.pk).delete()
            if os.path.exists(im.photo.path):
                os.remove(im.photo.path)

        success_url = reverse_lazy('profile:profile', kwargs={'username': self.request.user})
        success_msg = 'Запись удалена!'

        calc_start.delay(self.request.user.pk, self.kwargs['username'])
        get_best_five_summ.delay()
        return redirect(success_url, success_msg)

