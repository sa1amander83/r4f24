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
        calc_start.delay(self.request.user.pk, self.kwargs['username'])
        get_best_five_summ.delay()
        return redirect(success_url, success_msg)


class AddFamily(CreateView, LoginRequiredMixin):
    model = Group
    template_name = 'addfamily.html'
    form_class = AddFamilyForm
    success_url = reverse_lazy('profile:profile')

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        return context




def add_family(request, username):
    families = Group.objects.all()

    if request.method == 'POST' and Group.objects.filter(runner__runner_status=1):
        form = FamilyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile:family_list', request.user )





    else:
        form = FamilyForm()
    return render(request, 'add_family.html', {'form': form, 'families':families})

def family_list(request, username):
    families = Group.objects.all()

    return render(request, 'family_list.html', {'families': families, 'username':request.user.username})


def show_reset(request):
    form = ResetForm()
    if request.method == "POST":
        try:
            username_form = request.POST.get("username")
            password = request.POST.get("password1")
            password2 = request.POST.get("password2")
            key = request.POST.get("keyword")

            getTeam = Teams.objects.get(team=username_form[:3])

            keywordOfTeam = getTeam.keyword

            try:
                username = User.objects.get(username=username_form)
            except ObjectDoesNotExist:
                messages.error(request,
                               'Участник с таким номером не найден')
                render(request, 'pass_reset.html', {'form': form})

            if key != keywordOfTeam:
                messages.error(request,
                               'Неверно указано кодовое слово')
                render(request, 'pass_reset.html', {'form': form})

            if password != password2:
                messages.error(request,
                               'Введенные пароли не совпадают')
                render(request, 'pass_reset.html', {'form': form})

            if key.lower() == keywordOfTeam and User.objects.get(username=username_form) and password == password2:
                user = User.objects.get(username=username_form)
                print(user)

                user.set_password(password)
                user.save()
                return redirect('authorize:login')

        except:
            pass

    return render(request, 'pass_reset.html', {'form': form})


def show_reset_success(request):
    return render(request, 'pass_updated.html')




class MyGroup(ListView, DataMixin):
    model = Group
    template_name = 'groups.html'
    context_object_name = 'data'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        group_users = {}
        # поулчаем группу через юезра из кварг
        try:
            obj = User.objects.get(username=self.kwargs['username'])

            group = obj.runner_group
            if group is not None:
            # получаем всех пользователей с этой группой
                group_stat = User.objects.filter(runner_group=obj.runner_group)


                group_users[obj.runner_group] = []

                for user in group_stat:
                    stats_obj = Statistic.objects.get(runner_stat_id=obj.id)
                    group_users[obj.runner_group].append({
                        'group': str(group),
                        'user': user.username,
                        'total_distance': stats_obj.total_distance,
                        'total_time': stats_obj.total_time,
                        'total_average_temp': stats_obj.total_average_temp,
                        'total_days': stats_obj.total_days,
                        'total_runs': stats_obj.total_runs,
                        'total_balls': stats_obj.total_balls,
                        'is_qualificated': stats_obj.is_qualificated
                    })
                context['qs'] = group_users
            else:
                context['message']='Вы не состоите в группе'



        except:
            context['qs'] = None

        return context
#добавляем группу участнику если он в ней состоит
def addRunnerToGroup(request, username):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(User, id=request.user.id).runner_group

        if group:
            messages.warning(request, f'Вы уже входите  в эту группу: {group}.')
        else:
            group.runner_group=group_id
            messages.success(request, f'Вы создали и добавились в группу{group.group_title}.')
        return redirect('group_view', group_id=group.id)

    groups = Group.objects.all()
    return render(request, 'add_runner_to_group.html', {'groups': groups})




#отображение участников группы в профиле

# def my_group(request, username):
#
#     print(data)
#
#     return render(request, 'mygroup.html',data)