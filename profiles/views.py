import os

from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import redirect, render, get_object_or_404

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from core.models import User, Group, Teams
from profiles.models import RunnerDay, Statistic, Photo
from profiles.tasks import calc_start, get_best_five_summ, calc_comands

from profiles.utils import DataMixin
from r4f24.forms import RunnerDayForm, AddFamilyForm, FamilyForm, ResetForm

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from .models import RunnerDay, Statistic, Photo

from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from .models import RunnerDay, Statistic


class ProfileUser(ListView, DataMixin):
    model = RunnerDay
    template_name = 'profile.html'

    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_data'] = get_user_model().objects.filter(username=self.kwargs['username'])
        getuser = get_user_model().objects.get(username=self.kwargs['username'])

        try:
            getuser_stat = Statistic.objects.get(runner_stat__username=self.kwargs['username'])

            context['run_user'] = getuser.username
            context['exists_in_group'] = getuser.runner_group_id
            context['runner_group'] = Group.objects.get(id=getuser.runner_group_id).group_title
            context['runner_group_id'] = getuser.runner_group_id

            context['run_user_avg'] = getuser_stat.total_average_temp
            context['run_user_time'] = getuser_stat.total_time

        except ObjectDoesNotExist:
            context['runner_group'] = False
            getuser_stat = False

        get_category = getuser.runner_category

        context['runner_day'] = RunnerDay.objects.filter(runner__username=self.kwargs['username']).order_by(
            'day_select', 'time_create', 'number_of_run', 'run_url')

        photos = get_user_model().objects.get(username=self.kwargs['username'])
        context['images'] = photos.photos.all()

        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])
        context['runner_stat'] = self.kwargs['username']

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0


        #Всего бегунов
        context['total_runners'] = Statistic.objects.all().count()
        context['total_runners_category'] = Statistic.objects.filter(runner_stat__runner_category=get_category).count()

        runners_list = list(
            Statistic.objects.all().order_by('-total_balls').values_list('runner_stat__username', flat=True))

        runners_list_category = list(
            Statistic.objects.filter(runner_stat__runner_category=get_category).order_by('-total_balls').values_list(
                'runner_stat__username', flat=True))

        age_of_user = getuser.runner_age
        user_category= getuser.runner_category or None
        # Create a list of runners based on age categories
        runners_list_age_category = []

        # Define age ranges and filter runners accordingly
        if age_of_user < 17:
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__lt=17).order_by('-total_balls').values_list(
                    'runner_stat__username', flat=True))

            # Count participants in this age group
            context['count_age_and_category'] = Statistic.objects.filter(runner_stat__runner_age__lt=18
                                                                       , runner_stat__runner_category=user_category).count()

        elif 18 <= age_of_user <= 35:
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__gte=18, runner_stat__runner_age__lte=35).order_by(
                    '-total_balls').values_list('runner_stat__username', flat=True))

            # Count participants in this age group
            context['count_age_and_category'] = Statistic.objects.filter(runner_stat__runner_age__gte=18,
                                                                        runner_stat__runner_age__lte=35,
                                                                        runner_stat__runner_category=user_category).count()

        elif 36 <= age_of_user <= 49:
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__gte=36, runner_stat__runner_age__lte=49).order_by(
                    '-total_balls').values_list('runner_stat__username', flat=True))

            # Count participants in this age group
            context['count_age_and_category'] = Statistic.objects.filter(runner_stat__runner_age__gte=36,
                                                                        runner_stat__runner_age__lte=49,
                                                                        runner_stat__runner_category=user_category).count()

        else:  # age_of_user >= 50
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__gte=50).order_by('-total_balls').values_list(
                    'runner_stat__username', flat=True))

            # Count participants in this age group
            context['count_age_and_category'] = Statistic.objects.filter(runner_stat__runner_age__gte=50,
                                                                         runner_stat__runner_category=user_category).count()

        try:
            # Calculate places in different categories
            context['category_age_count'] = len(runners_list_age_category)

            # Place in total runners list
            context['place_in_total'] = runners_list.index(self.kwargs['username']) + 1

            # Place in age category
            if self.kwargs['username'] in runners_list_age_category:
                context['place_in_age_category'] = runners_list_age_category.index(self.kwargs['username']) + 1
            else:
                context['place_in_age_category'] = None

            # Place in category (general category)
            if self.kwargs['username'] in runners_list_category:
                context['place_in_category'] = runners_list_category.index(self.kwargs['username']) + 1
            else:
                context['place_in_category'] = None

        except ValueError:
            # Handle case where username not found in lists
            context['place_in_total'] = None
            context['place_in_age_category'] = None
            context['place_in_category'] = None

        obj = RunnerDay.objects.filter(runner__username=self.kwargs['username'])

        if len(obj) > 0:
            return dict(list(context.items()))

        else:
            context['user_data'] = get_user_model().objects.filter(username=self.kwargs['username'])
            context['tot_dist'] = {}

        return dict(list(context.items()))

class EditProfile(LoginRequiredMixin, UpdateView, DataMixin):
    model = User
    template_name = 'editprofile.html'
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.object.username})

    def get_object(self, queryset=None):
        return self.request.user

    fields = ['runner_age', 'runner_gender', 'zabeg22', 'zabeg23']


class InputRunnerDayData(DataMixin, LoginRequiredMixin, CreateView):
    form_class = RunnerDayForm
    template_name = 'day.html'
    success_url = reverse_lazy('profile:profile')
    model = RunnerDay

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        getuser = get_user_model().objects.get(username=self.kwargs['username'])
        context['runner_category'] = getuser.runner_category
        return context

    def form_valid(self, form):
        print(form.cleaned_data)
        dayselected = form.cleaned_data['day_select']

        # Проверяем количество пробежек на выбранный день
        runs_today = RunnerDay.objects.filter(
            runner__username=self.kwargs['username']
        ).filter(day_select=dayselected)
        first_run = runs_today.count()

        if first_run < 2:
            new_item = form.save(commit=False)
            userid = get_user_model().objects.get(username=self.kwargs['username'])
            new_item.runner_id = userid.id
            number_of_run = first_run + 1  # Соответствующий номер пробежки (1 или 2)

            # Создание самой пробежки
            runner_day = RunnerDay.objects.create(
                runner_id=userid.id,
                day_select=form.cleaned_data['day_select'],
                day_distance=form.cleaned_data['day_distance'],
                day_time=form.cleaned_data['day_time'].strftime('%H:%M:%S'),
                day_average_temp=form.cleaned_data['day_average_temp'],
                ball=form.cleaned_data['ball'],
                ball_for_champ=form.cleaned_data['ball_for_champ'],
                number_of_run=number_of_run,
                run_url=form.cleaned_data['run_url']
            )

            # Привязываем фотографии к пробежке
            for each in form.cleaned_data['photo']:
                Photo.objects.create(
                    runner_id=userid.id,
                    number_of_run=number_of_run,
                    day_select=dayselected,
                    photo=each,
                    runner_day=runner_day  # Связь с конкретной пробежкой
                )

            # Запуск задачи
            calc_start(self.request.user.pk, self.kwargs['username'])

            return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request, 'В день учитываются только две пробежки, '
                                         'обновите сведения по одной из пробежек')
            calc_start.delay(self.request.user.pk, self.kwargs['username'])
            return redirect('profile:profile', username=self.kwargs['username'])

    def form_invalid(self, form):
        messages.error(self.request, 'В день учитываются только две пробежки, '
                                     'обновите сведения по одной из пробежек')
        print(form.cleaned_data)
        calc_start.delay(self.request.user.pk, self.kwargs['username'])
        return redirect('profile:profile', username=self.kwargs['username'])



class EditRunnerDayData(LoginRequiredMixin, UpdateView, DataMixin):
    form_class = RunnerDayForm
    model = RunnerDay
    template_name = 'day.html'

    slug_url_kwarg = 'runner'
    login_url = reverse_lazy('index')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        getuser = get_user_model().objects.get(username=self.kwargs['username'])
        context['runner_category'] = getuser.runner_category
        return context

    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.kwargs['username']})

    def form_valid(self, form):
        self.obj = self.get_object()
        new_item = form.save(commit=False)
        userid = get_user_model().objects.get(id=self.request.user.id)

        new_item.runner_id = userid.id
        # Удаляем старые фотографии, привязанные к текущей пробежке
        old_photos = Photo.objects.filter(runner_day=self.obj)
        for photo in old_photos:
            if os.path.exists(photo.photo.path):
                os.remove(photo.photo.path)
            photo.delete()

        # Добавляем новые фотографии
        for each in form.cleaned_data['photo']:
            Photo.objects.create(
                runner_id=userid.id,
                day_select=self.obj.day_select,
                number_of_run=self.obj.number_of_run,
                photo=each,
                runner_day=self.obj
            )

        new_item.save()

        calc_start.delay(self.request.user.pk, self.kwargs['username'])

        return redirect('profile:profile', username=self.kwargs['username'])


class DeleteRunnerDayData(LoginRequiredMixin, DeleteView, DataMixin):
    model = RunnerDay
    template_name = 'deleteday.html'
    context_object_name = 'runday'

    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        self.object = self.get_object()
        runner_day_photos = Photo.objects.filter(runner_day=self.object)

        # Удаляем фотографии, привязанные к текущей пробежке
        for photo in runner_day_photos:
            if os.path.exists(photo.photo.path):
                os.remove(photo.photo.path)
            photo.delete()

        # Уяем текущую пробежку
        self.object.delete()

        success_url = self.get_success_url()
        calc_start.delay(self.request.user.pk, self.kwargs['username'])

        return redirect(success_url)



def zaglushka(request,username):
    return render(request, 'zaglushka.html')