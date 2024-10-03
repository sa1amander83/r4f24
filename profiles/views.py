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
            'day_select','time_create', 'number_of_run', 'run_url')

        photos = get_user_model().objects.get(username=self.kwargs['username'])
        context['images'] = photos.photos.all()

        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])
        context['runner_stat'] = self.kwargs['username']

        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0
        context['total_runners'] = Statistic.objects.all().count()
        context['total_runners_category'] = Statistic.objects.filter(runner_stat__runner_category=get_category).count()

        runners_list = list(
            Statistic.objects.all().order_by('-total_balls').values_list('runner_stat__username', flat=True))

        runners_list_category = list(
            Statistic.objects.filter(runner_stat__runner_category=get_category).order_by('-total_balls').values_list(
                'runner_stat__username', flat=True))

        age_of_user = getuser.runner_age

        # Create a list of runners based on age categories
        runners_list_age_category = []

        # Define age ranges and filter runners accordingly
        if age_of_user < 17:
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__lt=17).order_by('-total_balls').values_list(
                    'runner_stat__username', flat=True))

        elif 18 <= age_of_user <= 35:
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__gte=18, runner_stat__runner_age__lte=35).order_by(
                    '-total_balls').values_list(
                    'runner_stat__username', flat=True))
        elif 36 <= age_of_user <= 49:
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__gte=36, runner_stat__runner_age__lte=49).order_by(
                    '-total_balls').values_list(
                    'runner_stat__username', flat=True))
        else:  # age_of_user >= 50
            runners_list_age_category = list(
                Statistic.objects.filter(runner_stat__runner_age__gte=50).order_by('-total_balls').values_list(
                    'runner_stat__username', flat=True))


        try:
            context['category_age_count']=len(runners_list_age_category)
            context['place_in_total'] = runners_list.index(self.kwargs['username']) + 1
            context['place_in_age_category'] = runners_list_age_category.index(self.kwargs['username']) + 1
            context['place_in_category'] = runners_list_category.index(self.kwargs['username']) + 1
        except  BaseException:
            context['place'] = ''
        obj = RunnerDay.objects.filter(runner__username=self.kwargs['username'])
        context['tot_dist'] = Statistic.objects.all().order_by('-total_balls', 'total_distance')
        # place = stats.index(user_stat) + 1
        # context['runner_status'] = get_user_model().objects.filter(runner_status__gt=0)


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

        # Проверяем количество пробежек за день
        first_run_count = RunnerDay.objects.filter(runner__username=self.kwargs['username'],
                                                   day_select=dayselected).count()

        if first_run_count < 2:  # Если пробежек меньше двух
            new_item = form.save(commit=False)
            userid = get_user_model().objects.get(username=self.kwargs['username'])
            new_item.runner_id = userid.id

            # Номер пробежки
            number_of_run = first_run_count + 1

            # Сохраняем фотографии
            for each in form.cleaned_data['photo']:
                Photo.objects.create(
                    runner_id=userid.id,
                    number_of_run=number_of_run,
                    day_select=dayselected,
                    photo=each
                )

            # Сохраняем данные о пробежке
            RunnerDay.objects.create(
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

            # Вызываем асинхронную задачу
            calc_start.delay(self.request.user.pk, self.kwargs['username'])

            return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request, 'В день учитываются только две пробежки. '
                                         'Обновите сведения по одной из пробежек.')

            return redirect('profile:profile', username=self.kwargs['username'])

    def form_invalid(self, form):
        messages.error(self.request, 'Произошла ошибка при обработке формы.')
        print(form.cleaned_data)

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
        return reverse_lazy('profile:profile', kwargs={'runner': self.object})

    def form_valid(self, form):
        self.obj = self.get_object()
        new_item = form.save(commit=False)
        userid = get_user_model().objects.get(id=self.request.user.id)

        new_item.runner_id = userid.id
        dayselected = self.obj.day_select
        runs = self.obj.number_of_run

        # Fetch existing images for this run
        old_images = Photo.objects.filter(day_select=dayselected, number_of_run=runs)

        # Delete old images if necessary
        for im in old_images:
            if os.path.exists(im.photo.path):
                os.remove(im.photo.path)  # Remove file from filesystem
            im.delete()  # Delete the photo instance

        # Create new photos from the form data
        for each in form.cleaned_data['photo']:
            Photo.objects.create(
                runner_id=userid.id,
                day_select=dayselected,
                number_of_run=runs,
                photo=each
            )

        new_item.save()

        calc_start.delay(self.request.user.pk, self.kwargs['username'])

        return redirect('profile:profile', username=self.request.user)


class DeleteRunnerDayData(LoginRequiredMixin, DeleteView, DataMixin):
    model = RunnerDay
    template_name = 'deleteday.html'
    context_object_name = 'runday'

    def form_valid(self, form):
        self.object = self.get_object()
        get_runday = self.object.day_select  # Get day_select from the object being deleted
        get_number_run = self.object.number_of_run
        success_url = reverse_lazy('profile:profile', kwargs={'username': self.request.user})
        success_msg = 'Запись удалена!'

        try:
            # Delete the RunnerDay instance
            self.object.delete()

            # Find and delete all photos associated with this specific run
            old_images = Photo.objects.filter(day_select=get_runday, number_of_run=get_number_run)

            for old_image in old_images:
                if os.path.exists(old_image.photo.path):
                    os.remove(old_image.photo.path)  # Remove the file from the filesystem
                old_image.delete()  # Delete the photo instance

        except ObjectDoesNotExist:
            calc_start.delay(self.request.user.pk, self.kwargs['username'])
            return redirect(success_url)  # Removed success_msg as it won't work with redirect

        calc_start.delay(self.request.user.pk, self.kwargs['username'])

        return redirect(success_url)  # Removed success_msg as it won't work with redirect


def zaglushka(request, username):
    return render(request, 'zaglushka.html')