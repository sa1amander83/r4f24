import os
from django.db import IntegrityError
from django.http import HttpResponseBadRequest
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
from django.db.models import Q
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

        photos = Photo.objects.filter(runner_day__runner__username=self.kwargs['username'])
        context['images'] = photos
        context['data'] = Statistic.objects.filter(runner_stat__username=self.kwargs['username'])
        context['runner_stat'] = self.kwargs['username']
        runs = RunnerDay.objects.filter(runner__username=self.kwargs['username'])
        context['runs'] = runs
        if len(RunnerDay.objects.filter(runner__username=self.kwargs['username'])):
            context['haverun'] = 1
        else:
            context['haverun'] = 0


        #Всего бегунов
        context['total_runners'] = Statistic.objects.all().count()
        context['total_runners_category'] = Statistic.objects.filter(runner_stat__runner_category=get_category).count()

        runners_list = list(
            Statistic.objects.all().order_by('-total_balls').values_list('runner_stat__username', flat=True))
        #
        runners_list_category = list(
            Statistic.objects.filter(runner_stat__runner_category=get_category).order_by('-total_balls').values_list(
                'runner_stat__username', flat=True))

        age_of_user = getuser.runner_age
        gender=getuser.runner_gender
        # Create a list of runners based on age categories
        try:
            if age_of_user < 17:
                runners_age_filter = Q(runner_stat__runner_age__lte=17)
            elif 18 <= age_of_user <= 35:
                runners_age_filter = Q(runner_stat__runner_age__gte=18, runner_stat__runner_age__lte=35)
            elif 36 <= age_of_user <= 49:
                runners_age_filter = Q(runner_stat__runner_age__gte=36, runner_stat__runner_age__lte=49)
            else:
                runners_age_filter = Q(runner_stat__runner_age__gte=50)

            if get_category == 3:
                runners_list_age_category = Statistic.objects.filter(runners_age_filter, runner_stat__runner_gender='м',
                                                                     runner_stat__runner_category=3) \
                    .order_by('-total_balls_for_champ') \
                    .values_list('runner_stat__username', flat=True) \
                    .distinct()
                runners_list_category = Statistic.objects.filter(runner_stat__runner_category=3,
                                                                 runner_stat__runner_gender='м',) \
                    .order_by('-total_balls_for_champ') \
                    .values_list('runner_stat__username', flat=True) \
                    .distinct()
            else:
                runners_list_age_category = Statistic.objects.filter(runners_age_filter, runner_stat__runner_gender=gender,
                                                                     runner_stat__runner_category=get_category) \
                    .order_by('-total_balls') \
                    .values_list('runner_stat__username', flat=True) \
                    .distinct()
                runners_list_category = Statistic.objects.filter(runner_stat__runner_category=get_category,
                                                                 runner_stat__runner_gender=gender) \
                    .order_by('-total_balls') \
                    .values_list('runner_stat__username', flat=True) \
                    .distinct()

            runners_list_age = (Statistic.objects.filter(runners_age_filter, runner_stat__runner_gender=gender).
                                order_by('-total_balls').values_list('runner_stat__username', flat=True).distinct())

            runners_list = Statistic.objects.all().order_by('-total_balls').values_list('runner_stat__username',
                                                                                        flat=True)

            runners_list_age = list(runners_list_age)
            runners_list_age_category = list(runners_list_age_category)
            runners_list_category = list(runners_list_category)
            runners_list = list(runners_list)


            context['count_age_and_category'] = Statistic.objects.filter(runners_age_filter,runner_stat__runner_gender=gender,
                                                                         runner_stat__runner_category=get_category).count()

            context['total_runners'] = Statistic.objects.all().count()
            context['total_runners_category'] = Statistic.objects.filter(
                runner_stat__runner_category=get_category, runner_stat__runner_gender=gender).count()

            context['place_in_total'] = runners_list.index(self.kwargs['username']) + 1 if self.kwargs[
                                                                                               'username'] in runners_list else None
            context['place_in_category'] = runners_list_category.index(self.kwargs['username']) + 1 if self.kwargs[
                                                                                                           'username'] in runners_list_category else None
            context['place_in_age'] = runners_list_age.index(self.kwargs['username']) + 1 if self.kwargs[
                                                                                                 'username'] in runners_list_age else None
            context['place_in_age_category'] = runners_list_age_category.index(self.kwargs['username']) + 1 if \
            self.kwargs['username'] in runners_list_age_category else None

            context['category_age_count'] = len(runners_list_age_category)
            context['count_age'] = len(runners_list_age)


            #

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
        context['username'] = getuser.username

        return context

    def form_valid(self, form):
        print(form.cleaned_data)
        dayselected = form.cleaned_data['day_select']

        # Проверяем количество пробежек на выбранный день
        runs_today = RunnerDay.objects.filter(
            runner__username=self.kwargs['username'],
            day_select=dayselected
        )

        first_run = runs_today.count()

        if first_run < 2:
            try:
                userid = get_user_model().objects.get(username=self.kwargs['username'])
                get_team_id = userid.runner_team_id

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

                # Обновляем существующие фотографии и создаем новые при необходимости
                existing_photos = Photo.objects.filter(runner_day=runner_day)

                for index, each in enumerate(form.cleaned_data.get('photo', [])):
                    if index < len(existing_photos):
                        # Обновляем существующую фотографию
                        existing_photos[index].photo = each
                        existing_photos[index].save()
                    else:
                        # Создаем новую фотографию
                        Photo.objects.create(
                            runner=userid,

                            runner_day=runner_day,
                            photo=each
                        )

                # Удаляем лишние фотографии
                if len(existing_photos) > len(form.cleaned_data.get('photo', [])):
                    for excess_photo in existing_photos[len(form.cleaned_data.get('photo', [])):]:
                        if os.path.exists(excess_photo.photo.path):
                            try:
                                os.remove(excess_photo.photo.path)  # Удаляем файл из файловой системы
                            except Exception as e:
                                messages.error(self.request, f'Ошибка при удалении файла: {str(e)}')
                        excess_photo.delete()  # Удаляем запись из базы данных

                # Запуск задачи
                calc_start(self.request.user.pk, self.kwargs['username'])
                # calc_start.delay(self.request.user.pk, self.kwargs['username'])
                get_best_five_summ.delay(get_team_id)
                calc_comands(self.kwargs['username'])

                messages.success(self.request, 'Пробежка успешно добавлена!')
                return redirect('profile:profile', username=self.kwargs['username'])
            except IntegrityError as e:
                messages.error(self.request, 'Ошибка базы данных: ' + str(e))
                return redirect('profile:profile', username=self.kwargs['username'])
            except HttpResponseBadRequest as e:  # For 413 errors (Payload Too Large)
                messages.error(self.request, 'Ошибка: Вы пытаетесь загрузить слишком большие изображения.')
                return redirect('profile:profile', username=self.kwargs['username'])
            except Exception as e:
                messages.error(self.request, f'Произошла ошибка: {str(e)}')
                return redirect('profile:profile', username=self.kwargs['username'])
        else:
            messages.error(self.request, 'В день учитываются только две пробежки. '
                                         'Обновите сведения по одной из пробежек.')
            return redirect('profile:profile', username=self.kwargs['username'])

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при обработке формы.')
        print(form.cleaned_data)
        return redirect('profile:profile', username=self.kwargs['username'])


class EditRunnerDayData(LoginRequiredMixin, UpdateView):
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
        try:
            self.obj = self.get_object()
            new_item = form.save(commit=False)
            userid = get_user_model().objects.get(id=self.request.user.id)
            new_item.runner_id = userid.id

            # Получаем существующие фотографии для этой пробежки
            existing_photos = Photo.objects.filter(runner_day=self.obj)

            # Обновляем существующие фотографии и создаем новые при необходимости
            uploaded_photos = form.cleaned_data.get('photo', [])
            for index, each in enumerate(uploaded_photos):
                if index < len(existing_photos):
                    # Обновляем существующую фотографию
                    existing_photos[index].photo = each
                    existing_photos[index].save()
                else:
                    # Создаем новую фотографию и связываем с текущим объектом RunnerDay
                    Photo.objects.create(
                        runner_day=self.obj,  # Ensure we associate it with the correct RunnerDay instance
                        photo=each
                    )

            # Удаляем лишние фотографии, если их больше чем загруженных
            if len(existing_photos) > len(uploaded_photos):
                for excess_photo in existing_photos[len(uploaded_photos):]:
                    if os.path.exists(excess_photo.photo.path):
                        try:
                            os.remove(excess_photo.photo.path)  # Удаляем файл из файловой системы
                        except Exception as e:
                            messages.error(self.request, f'Ошибка при удалении файла: {str(e)}')
                    excess_photo.delete()  # Удаляем запись из базы данных

            new_item.save()
            # calc_comands.delay(self.kwargs['username'])
            calc_comands(self.kwargs['username'])
            # Запуск задач после успешного сохранения
            # calc_start.delay(self.request.user.pk, self.kwargs['username'])
            calc_start(self.request.user.pk, self.kwargs['username'])
            get_best_five_summ.delay(userid.runner_team_id)


            messages.success(self.request, 'Запись успешно обновлена!')
            return redirect(self.get_success_url())

        except Exception as e:
            messages.error(self.request, f'Произошла ошибка: {str(e)}')
            return redirect('profile:profile', username=self.request.user.username)

class DeleteRunnerDayData(LoginRequiredMixin, DeleteView):
    model = RunnerDay
    template_name = 'deleteday.html'
    context_object_name = 'runday'

    def get_success_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.request.user.username})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Получаем day_select и number_of_run для удаления связанных фотографий
        get_runday = self.object.day_select
        get_number_run = self.object.number_of_run
        userid = get_user_model().objects.get(id=self.request.user.id)
        get_team_id = userid.runner_team_id

        # Находим и удаляем все фотографии, связанные с этой пробежкой
        old_images = Photo.objects.filter(runner_day=self.object)

        for old_image in old_images:
            if os.path.exists(old_image.photo.path):
                try:
                    os.remove(old_image.photo.path)  # Удаляем файл из файловой системы
                except Exception as e:
                    messages.error(request, f'Ошибка при удалении файла: {str(e)}')
            old_image.delete()  # Удаляем запись из базы данных

        # Удаляем объект RunnerDay
        self.object.delete()

        calc_start(self.request.user.pk, self.kwargs['username'])
        # calc_start.delay(self.request.user.pk, self.kwargs['username'])
        get_best_five_summ.delay(get_team_id)
        # calc_comands.delay(self.kwargs['username'])
        calc_comands(self.kwargs['username'])
        messages.success(request, 'Запись успешно удалена!')

        return redirect(self.get_success_url())

def zaglushka(request,username):
    return render(request, 'zaglushka.html')